from pyrogram import Client

app = Client(
    "user_session",
    api_id=25066187,
    api_hash="4cbb616dea66bf2b8ea81c6bc571a8ce"
)

app.start()
print("\n\n✅ YOUR SESSION STRING:")
print(app.export_session_string())
print("\n")
app.stop()