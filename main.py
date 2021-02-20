#!/usr/bin/env python3
import requests, logging, re
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext, InlineQueryHandler
from telegram.ext.filters import Filters
from telegram.error import InvalidToken
from telegram import ParseMode, Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.utils.helpers import escape_markdown as EM
from uuid import uuid4
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s[%(name)s] %(message)s")
log = logging.getLogger("MainScript")

S = requests.Session()

URL = "https://zh.wikipedia.org/w/api.php"

def shorttxt(txt,l):
    return (txt[:l] + '..') if len(txt) > l else txt

def pwtxt(S,wtxt): # TextWikiPlus coding style, can merge into textwikiplus
    """
    parse.py

    Modify From MediaWiki API Demos
    https://www.mediawiki.org/wiki/API:Parsing_wikitext/zh

    Origional License: MIT License
    """
    PARAMS = {
        "action": "parse",
        "text": wtxt,
        "contentmodel": "wikitext",
        "format": "json",
    }
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    return (DATA["parse"]["text"]["*"])

def cmd(update: Update, context: CallbackContext):
    log.info("Got pwtxt command!")
    if len(context.args) == 0:
        update.message.reply_text("Not enough args\!",parse_mode=ParseMode.MARKDOWN_V2)
        return
    rt = re.search('<div class=\"mw-parser-output\">((.|\r|\n)*)</div>', re.sub("<!-- \nNewPP(.|\r|\n)*-->", "", pwtxt(S," ".join(context.args)))).group(1)
    update.message.reply_text(shorttxt(rt,400))

def token():
    try:
        with open("token.txt","r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        log.error("No token.txt!")
        # print("[ERROR] No token.txt!")
        exit(3)

def iQ(update: Update, context: CallbackContext) -> None:
    context = update.inline_query.query
    log.info("Inline mode!")
    if len(context) == 0:
        update.inline_query.answer([InlineQueryResultArticle(id=uuid4(), title="No wikitext!", input_message_content=InputTextMessageContent("No wikitext!")),])
        return
    rt = re.search('<div class=\"mw-parser-output\">((.|\r|\n)*)</div>', re.sub("<!-- \nNewPP(.|\r|\n)*-->", "", pwtxt(S,context))).group(1)
    results = [
        InlineQueryResultArticle(
            id=uuid4(), title="Parser", input_message_content=InputTextMessageContent("**Origional: **" + EM(context,2) + "\n\n**Parsed text: **" + EM(shorttxt(rt,400),2),parse_mode=ParseMode.MARKDOWN_V2)
        ),
    ]
    update.inline_query.answer(results)


def main():
    """Start the bot."""
    tok = token()
    try:
        updater = Updater(tok, use_context=True)
        log.info("Get updater success!")
    except InvalidToken:
        log.critical("Invalid Token! Plase edit token.txt and fill in a valid token.")
        raise
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('pwtxt', cmd))
    dp.add_handler(InlineQueryHandler(iQ))
    updater.start_polling()
    log.info("Started the bot! Use Ctrl-C to stop it.")
    updater.idle()

if __name__ == '__main__':
    main()
