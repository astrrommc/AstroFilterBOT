# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from os import environ
from typing import Dict, Optional

class TokenParser:
    def __init__(self, config_file: Optional[str] = None):
        self.tokens = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        """
        Maximizes speed by pulling all tokens starting with 'MULTI_TOKEN' 
        from your environment variables.
        """
        # Optimized filtering to catch MULTI_TOKEN1, MULTI_TOKEN2, etc.
        self.tokens = dict(
            (c + 1, t)
            for c, (_, t) in enumerate(
                filter(
                    lambda n: n[0].startswith("MULTI_TOKEN") and re.match(r'\d+:[A-Za-z0-9_-]{35}', n[1]), 
                    sorted(environ.items())
                )
            )
        )
        
        # If no MULTI_TOKEN found, check if you used the space-separated list we discussed
        if not self.tokens:
            multi_list = environ.get("MULTI_TOKENS", "").split()
            for index, token in enumerate(multi_list, start=1):
                if re.match(r'\d+:[A-Za-z0-9_-]{35}', token):
                    self.tokens[index] = token

        return self.tokens