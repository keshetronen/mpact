from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


def validate_phone(username):
    if username[0] != "+":
        raise ValidationError("Phone number should start with '+'.")
    return username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number is invalid.",
    )
    phone = models.CharField(max_length=20, validators=[phone_regex, validate_phone])


class ChatBase(models.Model):
    """
    Represents a telegram chat, which could be a group or 1:1 chat (individual)
    """
    id = models.IntegerField(primary_key=True, help_text='The Telegram ID of the chat')
    messages_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class GroupChat(ChatBase):
    """
    Represents a telegram group
    """
    title = models.TextField()
    participant_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} - {self.title}"


class Bot(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField(null=True)
    chats = models.ManyToManyField(GroupChat, through="ChatBot")

    def __str__(self):
        return f"{self.id} - {self.username}"


class ChatBot(models.Model):
    chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)

    def __str__(self):
        return f"chat_id: {self.chat.id} - bot_username: {self.bot.username}"


class IndividualChat(ChatBase):
    """
    Represents a telegram 1:1 conversation.
    """
    username = models.TextField(null=True)
    first_name = models.TextField()
    last_name = models.TextField(null=True)
    access_hash = models.TextField()
    study_id = models.TextField(null=True)
    age = models.IntegerField(null=True)
    gender = models.TextField(null=True)
    address = models.TextField(null=True)
    notes = models.TextField(null=True)
    bots = models.ManyToManyField(Bot, through="BotIndividual")

    def __str__(self):
        return f"{self.id} - {self.first_name}"


class BotIndividual(models.Model):
    bot = models.ForeignKey(
        Bot, related_name="bot_individuals", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(IndividualChat, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"individual_id: {self.individual.id} - bot_username: {self.bot.username}"
        )


class Message(models.Model):
    telegram_msg_id = models.IntegerField()
    sender_id = models.IntegerField()
    sender_name = models.TextField()
    room_id = models.IntegerField()
    message = models.TextField(null=True)
    date = models.DateTimeField(default=timezone.now)
    from_group = models.BooleanField()
    is_flagged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.room_id} - {self.sender_name} - {self.message}"


class FlaggedMessage(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    group_id = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.message.id} - {self.message.room_id}"


class UserChatUnread(models.Model):
    user_id = models.IntegerField()
    room_id = models.IntegerField()
    unread_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user_id", "room_id")

    def __str__(self):
        return f"{self.user_id} - {self.room_id} - {self.unread_count}"
