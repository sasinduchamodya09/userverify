from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- SETTINGS ---
MAIN_GROUP_ID = -1002598293899  # ⚠️ main group id
MAIN_GROUP_LINK = "https://t.me/+XbqX4V_K2WhhMDQ1"  # ⚠️ main group link
NEW_GROUP_LINK = "https://t.me/+jRahWWFRkII0ZWRl"    # ⚠️ verified group link
OWNER_ID = 7724407419 # ⚠️ මෙතනට ඔයාගේ Telegram ID එක දාන්න (Bot owner id)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "User"

    # 🔹 Always send welcome message
    await update.message.reply_text(
        f"👋 Hello {first_name}!\nWelcome to our verification bot.\nLet's verify your account step by step."
    )

    # 🔹 Check group membership
    try:
        chat_member = await context.bot.get_chat_member(MAIN_GROUP_ID, user.id)

        if chat_member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text(
                "✅ You are already in our main group.\nYou almost done, to verify please send your photo 📸"
            )
            context.user_data["awaiting_photo"] = True
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Group", url=MAIN_GROUP_LINK)]
            ])
            await update.message.reply_text(
                "⚠️ You must join our main group first using the button below 👇 then type /start again.",
                reply_markup=keyboard
            )

    except Exception:
        await update.message.reply_text(
            "⚠️ Couldn't check your group membership.\nMake sure the bot is added to your group as an admin."
        )

# --- HANDLE PHOTO (Verification Step) ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not context.user_data.get("awaiting_photo"):
        await message.reply_text("Please send photo again after press /start")
        return

    # 🔹 Detect if the photo is view-once / protected
    if message.has_protected_content:
        await message.reply_text(
            "⚠️ This looks like a *view-once* or *protected* photo.\n\n"
            "Please send a **normal photo** (not view-once) so we can verify you. 📸"
        )
        return

    # 🔹 Get highest-quality photo
    photo = message.photo[-1]

    # 🔹 Send confirmation message to user
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Request to Group", url=NEW_GROUP_LINK)]
    ])
    await message.reply_text(
        "📸 Your verification photo received!\n"
        "✅ Your verification is being processed.\n"
        "Please request to join the verified group using the button below.\n\nThank you ❤️",
        reply_markup=keyboard
    )

    # 🔹 Send photo to owner
    try:
        profile_link = (
            f"https://t.me/{user.username}" if user.username
            else f"tg://user?id={user.id}"
        )

        caption = (
            f"📥 *New Verification Request*\n"
            f"👤 Name: {user.first_name or ''} {user.last_name or ''}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"🔗 Profile: [{user.first_name or user.username or user.id}]({profile_link})"
        )

        await context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=photo.file_id,
            caption=caption,
            parse_mode="Markdown"
        )
        print("✅ Photo sent to owner successfully.")
    except Exception as e:
        print("❌ Error sending photo to owner:", e)

    context.user_data["photo_received"] = True
    context.user_data["awaiting_photo"] = False
    
    #else:
        #await update.message.reply_text("Please start verification using /start")

# --- HANDLE OTHER MESSAGES ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_photo"):
        await update.message.reply_text("⚠️ Please send your photo first 📷")
    else:
        await update.message.reply_text("Use /start to begin verification.")

# --- WHEN USER ADDED TO GROUP ---
async def when_user_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        try:
            await context.bot.send_message(
                chat_id=member.id,
                text="✅ You were added to the group successfully!"
            )
        except Exception as e:
            print("❌ Can't message user:", e)


# --- WHEN USER ADDED TO GROUP ---
async def when_user_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # ✅ Check if it's the VERIFIED group
    if chat_id == -1003224730440:  # <-- මෙතනට ඔයාගේ verified group ID එක දාන්න
        for member in update.message.new_chat_members:
            try:
                # Send private message to user
                await context.bot.send_message(
                    chat_id=member.id,
                    text="✅ You were successfully added to the verified group!\n\nWelcome aboard 🎉"
                )
                print(f"✅ Message sent to {member.id}")
            except Exception as e:
                print(f"❌ Can't message user {member.id}:", e)


# --- MAIN FUNCTION ---
def main():
    app = ApplicationBuilder().token("8591753824:AAE3Mh7MdK-E0SVrWOmUdT-0BCh_qjYkmJM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, when_user_added))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()