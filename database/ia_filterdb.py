import re, base64
from struct import pack
from pyrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from info import FILE_DB_URI, SEC_FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME, MULTIPLE_DATABASE, USE_CAPTION_FILTER, MAX_B_TN

# First Database
client = AsyncIOMotorClient(FILE_DB_URI)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

# Second Database
sec_client = AsyncIOMotorClient(SEC_FILE_DB_URI)
sec_db = sec_client[DATABASE_NAME]
sec_col = sec_db[COLLECTION_NAME]

vjdb = db
sec_db = sec_db


async def create_indexes():
    """Create indexes for faster search - call once on bot start"""
    await col.create_index([("file_name", "text")])
    await col.create_index("file_id", unique=True)
    await sec_col.create_index([("file_name", "text")])
    await sec_col.create_index("file_id", unique=True)
    print("Database indexes created successfully.")


async def save_file(media):
    """Save file in the database."""
    file_id = unpack_new_file_id(media.file_id)
    file_name = clean_file_name(media.file_name)
    new_file_name = f"@Astro_AF_bot {file_name}"

    file = {
        'file_id': file_id,
        'file_name': new_file_name,
        'file_size': media.file_size,
        'caption': media.caption.html if media.caption else None
    }

    if await is_file_already_saved(file_id, file_name):
        return False, 0

    try:
        await col.insert_one(file)
        print(f"{file_name} is successfully saved.")
        return True, 1
    except DuplicateKeyError:
        print(f"{file_name} is already saved.")
        return False, 0
    except Exception as e:
        if MULTIPLE_DATABASE:
            try:
                await sec_col.insert_one(file)
                print(f"{file_name} is successfully saved.")
                return True, 1
            except DuplicateKeyError:
                print(f"{file_name} is already saved.")
                return False, 0
        else:
            print(f"Error saving file: {e}")
            return False, 2


def clean_file_name(file_name):
    """Clean and format the file name."""
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name))
    unwanted_chars = ['[', ']', '(', ')', '{', '}']
    for char in unwanted_chars:
        file_name = file_name.replace(char, '')
    return ' '.join(filter(
        lambda x: not x.startswith('@') and not x.startswith('http')
        and not x.startswith('www.') and not x.startswith('t.me'),
        file_name.split()
    ))


async def is_file_already_saved(file_id, file_name):
    """Check if the file is already saved in either collection."""
    for collection in [col, sec_col]:
        if await collection.find_one({'file_id': file_id}) or await collection.find_one({'file_name': file_name}):
            return True
    return False


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query

    filter_query = {'file_name': regex}
    files = []

    if MULTIPLE_DATABASE:
        cursor1 = col.find(filter_query).sort('$natural', -1).skip(offset).limit(max_results)
        cursor2 = sec_col.find(filter_query).sort('$natural', -1).skip(offset).limit(max_results)
        async for file in cursor1:
            files.append(file)
        async for file in cursor2:
            files.append(file)
        total_results = await col.count_documents(filter_query) + await sec_col.count_documents(filter_query)
    else:
        cursor = col.find(filter_query).sort('$natural', -1).skip(offset).limit(max_results)
        async for file in cursor:
            files.append(file)
        total_results = await col.count_documents(filter_query)

    next_offset = "" if (offset + max_results) >= total_results else (offset + max_results)
    return files, next_offset, total_results


async def get_bad_files(query, file_type=None, use_filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = rf'(\b|[.+-_]){query}(\b|[.+-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[s.+-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return [], 0

    filter_criteria = {'file_name': regex}
    if USE_CAPTION_FILTER:
        filter_criteria = {'$or': [filter_criteria, {'caption': regex}]}

    total_results = await col.count_documents(filter_criteria)
    if MULTIPLE_DATABASE:
        total_results += await sec_col.count_documents(filter_criteria)

    files = []
    async for file in col.find(filter_criteria):
        files.append(file)
    if MULTIPLE_DATABASE:
        async for file in sec_col.find(filter_criteria):
            files.append(file)

    return files, total_results


async def get_file_details(query):
    result = await col.find_one({'file_id': query})
    if not result:
        result = await sec_col.find_one({'file_id': query})
    return result


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id