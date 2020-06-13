import discord
import json
import html
import logging
import requests
import random
import asyncio

from config.running_options import LOG_LEVEL

logging.basicConfig(
    filename="logs/trivia.log",
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# this game has been made with the open trivia db API : https://opentdb.com/
# All data provided by the API is available under the Creative Commons Attribution-ShareAlike 4.0 International License.
MAX_QUESTIONS = 1001
SETUP_TIMEOUT = 30.0
ANSWER_TIMEOUT = 60.0


class TriviaInstance:
    """Init Trivia game with the number of questions, their category, difficulty and type (boolean or multiple)"""

    def __init__(self, my_bot, channel, author, categories, mode):
        self.bot = my_bot
        self.questions_nb = ""
        self.categories = categories
        self.category = ""
        self.difficulty = ""
        self.type = ""
        self.players = []
        self.mode = mode
        self.channel = channel
        self.game_creator = author
        self.joinable = False
        self.keep_playing = True

    def set_category(self, new_category):
        for i in self.categories:
            if new_category == i["nbr"]:
                self.category = i["id"]
                return

    def set_difficulty(self, new_difficulty):
        self.difficulty = new_difficulty

    def set_type(self, new_type):
        self.type = new_type

    def set_mode(self, new_mode):
        self.mode = new_mode

    def stop_playing(self):
        self.keep_playing = False

    def init_game(self):
        question_url = "https://opentdb.com/api.php"
        questions_numb = int(self.questions_nb)
        questions = []
        while questions_numb > 0:
            if questions_numb > 49:
                request_question = "49"
            else:
                request_question = str(questions_numb)
            param = {
                "amount": request_question,
                "category": self.category,
                "difficulty": self.difficulty,
                "type": self.type,
            }
            # duplicates are not handled
            new_request = json.loads(
                (requests.get(url=question_url, params=param)).text
            )["results"]
            questions += new_request
            questions_numb -= 49

        return questions

    def is_player_registered(self, player):
        for p in self.players:
            if player == p.playerid:
                return p
        return False

    async def player_turn_join(self, ctx, author):
        if not self.joinable:
            await self.bot.send_message(
                ctx,
                author.mention + " sorry but it's either too late or "
                "there's no game in preparation.",
            )
            return
        if self.is_player_registered(author):
            await self.bot.send_message(
                ctx,
                author.mention + " you are already registered for this party, baka!",
            )
            return
        self.players.append(TriviaPlayer(author))
        await self.bot.send_message(ctx, author.mention + " joins the battle!")

    async def player_quit(self, ctx, author):
        for player in self.players:
            if player.playerid == author:
                self.players.remove(player)
                await self.bot.send_message(
                    ctx, player.playerid.mention + " left the game!"
                )
                return
        await self.bot.send_message(
            ctx, author.mention + " you are currently not in any party on this channel."
        )

    async def allow_join(self, ctx):
        self.joinable = True
        await asyncio.sleep(SETUP_TIMEOUT)
        self.joinable = False
        await self.bot.send_message(ctx, "Game starting!")
        await self.set_questions_nb(self.questions_nb * len(self.players))
        await self.start_turns_game(ctx=ctx)

    async def set_questions_nb(self, new_questions_nb):
        self.questions_nb = int(new_questions_nb)

    async def get_params(self, ctx):
        def is_cat(msg):
            if msg.channel != self.channel or msg.author != self.game_creator:
                return False
            if msg.content.lower() == "any":
                return True
            return is_natural_nbr(msg.content) and int(msg.content) in range(
                1, len(self.categories) + 1
            )

        def is_dif(msg):
            if msg.channel != self.channel or msg.author != self.game_creator:
                return False
            return msg.content.lower() in ["easy", "medium", "hard", "any"]

        def is_type(msg):
            if msg.channel != self.channel or msg.author != self.game_creator:
                return False
            return msg.content.lower() in ["boolean", "multiple", "any"]

        def is_natural(msg):
            if msg.channel != self.channel or msg.author != self.game_creator:
                return False
            try:
                nbr = int(msg.content)
                return 0 < nbr < MAX_QUESTIONS
            except ValueError:
                return False

        prefix = await self.bot.get_prefix(ctx.message)
        # CATEGORIES
        await self.bot.send_message(
            ctx,
            f"Specify a category number: (use '{prefix}trivia categories' to display categories) or "
            "type 'any' for random.",
        )
        try:
            category = await self.bot.wait_for(
                "message", check=is_cat, timeout=SETUP_TIMEOUT
            )
        except asyncio.TimeoutError:
            await self.gamed_timed_out(ctx=ctx)
            return
        if category.content.lower() != "any":
            self.set_category(int(category.content))

        # DIFFICULTY
        await self.bot.send_message(
            ctx, "Specify a difficulty: 'easy', 'medium', 'hard' or 'any'."
        )
        try:
            difficulty = await self.bot.wait_for(
                "message", check=is_dif, timeout=SETUP_TIMEOUT
            )
        except asyncio.TimeoutError:
            await self.gamed_timed_out(ctx=ctx)
            return
        if difficulty.content.lower() != "any":
            self.set_difficulty(difficulty.content)

        # QUESTION TYPE
        await self.bot.send_message(
            ctx, "Specify a question type: 'boolean', 'multiple' or 'any'."
        )
        try:
            new_type = await self.bot.wait_for(
                "message", check=is_type, timeout=SETUP_TIMEOUT
            )
        except asyncio.TimeoutError:
            await self.gamed_timed_out(ctx=ctx)
            return
        if new_type.content.lower() != "any":
            self.set_type(new_type.content.lower())

        # TURN MODE
        if self.mode == "turn":
            await self.bot.send_message(ctx, "How many questions per players?")
            try:
                question_answer = await self.bot.wait_for(
                    "message", check=is_natural, timeout=SETUP_TIMEOUT
                )
            except asyncio.TimeoutError:
                await self.gamed_timed_out(ctx=ctx)
                return
            await self.bot.send_message(
                ctx,
                "Parameters completed! Each person that now wants to join the game has 30 seconds to use"
                f" {prefix}trivia join on this channel to participate to the upcoming game",
            )
            await self.set_questions_nb(int(question_answer.content))
            await self.allow_join(ctx=ctx)

        # TIME MODE
        else:
            await self.bot.send_message(ctx, "How many questions?")
            try:
                question_answer = await self.bot.wait_for(
                    "message", check=is_natural, timeout=SETUP_TIMEOUT
                )
            except asyncio.TimeoutError:
                await self.gamed_timed_out(ctx=ctx)
                return
            await self.set_questions_nb(question_answer.content)
            await self.stat_time_game(ctx=ctx)

    async def start_turns_game(self, ctx):
        questions = self.init_game()
        question_number = 1
        player_index = 0
        if len(self.players) < 1:
            await self.bot.send_message(ctx, "No one joined the game, cancelling...")
            return
        for question in questions:
            if not self.keep_playing:
                await self.bot.send_message(
                    ctx, f"Game cancelled by {self.game_creator.mention}."
                )
                return
            # skip player turn and his question if he left the game
            if player_index >= len(self.players):
                player_index = 0
            await self.ask_target_question(
                ctx, self.players[player_index], question, question_number
            )
            player_index += 1
            question_number += 1
        await self.bot.send_message(ctx, "Game is over! Here's the leaderboard:")
        await self.display_leaderboard(ctx=ctx)

    async def stat_time_game(self, ctx):
        await self.bot.send_message(
            ctx,
            "In this mode, the first one that answers correctly wins a point but each"
            " player has only one try per question, be careful!",
        )
        questions = self.init_game()
        question_nb = 1
        for question in questions:
            if not self.keep_playing:
                await self.bot.send_message(
                    ctx, f"Game cancelled by {self.game_creator.mention}."
                )
                return
            failed_players = []
            answers_list = question["incorrect_answers"]
            answers_list.append(question["correct_answer"])
            random.shuffle(answers_list)
            if question["type"] == "multiple":
                answers = f"1) {answers_list[0]}\n2) {answers_list[1]}\n3) {answers_list[2]}\n4) {answers_list[3]}"
            else:
                answers = "\n".join(answers_list)
            await self.display_question(ctx, question, question_nb, answers)
            if question["type"] == "multiple":

                def is_correct_multiple_answer(msg):
                    if msg.channel != self.channel:
                        return False
                    if msg.author in failed_players:
                        return False
                    failed_players.append(msg.author)
                    return is_acceptable_answer(msg) and self.is_answer_correct(
                        question, msg.content, answers_list
                    )

                try:
                    player_answer = await self.bot.wait_for(
                        "message",
                        check=is_correct_multiple_answer,
                        timeout=ANSWER_TIMEOUT,
                    )
                except asyncio.TimeoutError:
                    await self.bot.send_message(
                        ctx, "Looks like everyone was scared to answer that question"
                    )
                    question_nb += 1
                    continue
            else:

                def is_correct_boolean_answer(msg):
                    if msg.channel != self.channel:
                        return False
                    if msg.author in failed_players:
                        return False
                    failed_players.append(msg.author)
                    return (
                        is_boolean_answer(msg)
                        and msg.content.lower() == question["correct_answer"].lower()
                    )

                try:
                    player_answer = await self.bot.wait_for(
                        "message",
                        check=is_correct_boolean_answer,
                        timeout=ANSWER_TIMEOUT,
                    )
                except asyncio.TimeoutError:
                    await self.bot.send_message(
                        ctx, "Looks like everyone was scared to answer that question"
                    )
                    question_nb += 1
                    continue

            await self.bot.send_message(
                ctx, "Correct! " + player_answer.author.mention + " wins 1 point!"
            )
            player = self.is_player_registered(player_answer.author)
            if not player:
                self.players.append(TriviaPlayer(player_answer.author))
                self.players[len(self.players) - 1].add_point()
            else:
                player.add_point()
            question_nb += 1
        await self.bot.send_message(ctx, "Game is over! Here's the leaderboard:")
        await self.display_leaderboard(ctx=ctx)

    async def display_question(self, ctx, question, question_nb, answers):
        embed = discord.Embed(colour=0x4C4CFF)
        embed.add_field(name="Question n°", value=f"{question_nb}/{self.questions_nb}")
        embed.add_field(name="Category:", value=html.unescape(question["category"]))
        embed.add_field(
            name="Question: ", value=f"**{html.unescape(question['question'])}**"
        )
        embed.add_field(
            name="Possible answers: ", value=html.unescape(answers), inline=False
        )
        await self.bot.send_message(ctx, embed=embed)

    async def ask_target_question(self, ctx, player, question, question_nb):
        def is_multiple_acceptable(msg):
            if msg.channel != self.channel or msg.author != player.playerid:
                return False
            return is_acceptable_answer(msg)

        def is_boolean_acceptable(msg):
            if msg.channel != self.channel:
                return False
            return is_boolean_answer(msg)

        answers_list = question["incorrect_answers"]
        answers_list.append(question["correct_answer"])
        random.shuffle(answers_list)
        if question["type"] == "multiple":
            answers = f"1) {answers_list[0]}\n2) {answers_list[1]}\n3) {answers_list[2]}\n4) {answers_list[3]}"
        else:
            answers = "\n".join(answers_list)
        await self.bot.send_message(
            ctx, player.playerid.mention + " this question is for you:"
        )
        await self.display_question(ctx, question, question_nb, answers)
        try:
            if question["type"] == "multiple":
                player_answer = await self.bot.wait_for(
                    "message", check=is_multiple_acceptable, timeout=ANSWER_TIMEOUT
                )
            else:
                player_answer = await self.bot.wait_for(
                    "message", check=is_boolean_acceptable, timeout=ANSWER_TIMEOUT
                )
        except asyncio.TimeoutError:
            await self.bot.send_message(
                ctx, "The question was apparently too complicated."
            )
            return
        if self.is_answer_correct(
            question, player_answer.content.lower(), answers_list
        ):
            player.add_point()
            await self.bot.send_message(
                ctx,
                f"{player.playerid.mention} correct! You win 1 point. Current score: {player.score}",
            )
        else:
            await self.bot.send_message(
                ctx,
                f"{player.playerid.mention} wrong! The correct answer was: {html.unescape(question['correct_answer'])}."
                f" Current score: {player.score}",
            )

    async def display_leaderboard(self, ctx):
        embed = discord.Embed(colour=0x4C4CFF)
        p = 0
        long_ass_string = ""
        if len(self.players) > 0:
            self.players.sort(key=lambda x: x.score, reverse=True)
            while p < 10 and p < len(self.players):
                plural = "s"
                if self.players[p].score == 1:
                    plural = ""
                long_ass_string += f"{self.players[p].playerid}: {self.players[p].score} point{plural}.\n"
                p += 1
            embed.add_field(name="Trivia Leaderboard", value=long_ass_string)
            await self.bot.send_message(ctx, embed=embed)

    async def gamed_timed_out(self, ctx):
        logging.debug(f"Trivia: instance creation on {self.channel} timed out.")
        await self.bot.send_message(ctx, "Game creation timed out :sob:")
        return

    @staticmethod
    def is_answer_correct(question, answer, answers_list):
        if is_natural_nbr(answer):
            if answers_list[int(answer) - 1] == question["correct_answer"]:
                return True
        return answer == question["correct_answer"].lower()


def is_acceptable_answer(msg):
    try:
        nbr = int(msg.content)
        return 1 <= nbr <= 4
    except ValueError:
        return False


def is_boolean_answer(msg):
    return msg.content.lower() in ["true", "false"]


def is_natural_nbr(msg):
    return msg.isdigit() and int(msg) > 0


class TriviaPlayer:
    def __init__(self, playerid):
        self.playerid = playerid
        self.score = 0

    def add_point(self):
        self.score += 1
