import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from loguru import logger
import json
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logger.add("bot.log", rotation="1 day", retention="7 days")

class ComfyUIBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not found in environment variables")
        
        # Load workflows
        self.workflows_path = Path("workflows")
        self.workflows = self._load_workflows()
        
    def _load_workflows(self):
        """Load all workflow JSON files from the workflows directory"""
        workflows = {}
        if not self.workflows_path.exists():
            self.workflows_path.mkdir(exist_ok=True)
            logger.info(f"Created workflows directory at {self.workflows_path}")
            return workflows
            
        for workflow_file in self.workflows_path.glob("*.json"):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflows[workflow_file.stem] = json.load(f)
                logger.info(f"Loaded workflow: {workflow_file.name}")
            except Exception as e:
                logger.error(f"Error loading workflow {workflow_file}: {e}")
        return workflows

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        keyboard = []
        for workflow_name in self.workflows.keys():
            keyboard.append([InlineKeyboardButton(workflow_name, callback_data=f"workflow_{workflow_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome to ComfyUI Bot! Please select a workflow:",
            reply_markup=reply_markup
        )

    async def handle_workflow_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle workflow selection"""
        query = update.callback_query
        await query.answer()
        
        workflow_name = query.data.replace("workflow_", "")
        if workflow_name in self.workflows:
            context.user_data['selected_workflow'] = workflow_name
            await query.edit_message_text(
                f"Selected workflow: {workflow_name}\nPlease send your prompt or image."
            )
        else:
            await query.edit_message_text("Workflow not found. Please try again.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages (text prompts or images)"""
        if 'selected_workflow' not in context.user_data:
            keyboard = []
            for workflow_name in self.workflows.keys():
                keyboard.append([InlineKeyboardButton(workflow_name, callback_data=f"workflow_{workflow_name}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Please select a workflow first:",
                reply_markup=reply_markup
            )
            return

        # TODO: Implement ComfyUI processing logic here
        await update.message.reply_text("Processing your request... (Implementation pending)")

    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_workflow_selection))
        application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, self.handle_message))

        # Start the bot
        logger.info("Starting bot...")
        application.run_polling()

if __name__ == "__main__":
    bot = ComfyUIBot()
    bot.run()
