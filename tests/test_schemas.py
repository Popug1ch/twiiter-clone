import pytest
from app.schemas.tweet import (
    TweetCreate,
    TweetsFeedResponse,
    TweetInFeed,
    Author,
    LikeUser,
)
from app.schemas.user import User, ProfileUser, ProfileResponse


class TestTweetSchemas:
    def test_tweet_create_valid(self):
        tweet = TweetCreate(tweet_data="Тест")
        assert tweet.tweet_data == "Тест"
        assert tweet.tweet_media_ids is None

    def test_tweet_create_with_media(self):
        tweet = TweetCreate(tweet_data="Тест", tweet_media_ids=[1, 2, 3])
        assert tweet.tweet_media_ids == [1, 2, 3]

    def test_tweet_create_empty_allowed(self):
        tweet = TweetCreate(tweet_data="")
        assert tweet.tweet_data == ""

    def test_tweet_in_feed_full(self):
        author = Author(id=1, name="Иван")
        like_user = LikeUser(user_id=2, name="Мария")

        tweet = TweetInFeed(
            id=1,
            content="Твит",
            attachments=["/static/media/1.jpg"],
            author=author,
            likes=[like_user],
        )
        assert tweet.id == 1
        assert tweet.author.name == "Иван"
        assert len(tweet.likes) == 1

    def test_tweets_feed_response(self):
        author = Author(id=1, name="Автор")
        tweet = TweetInFeed(
            id=1, content="Твит", attachments=[], author=author, likes=[]
        )
        resp = TweetsFeedResponse(result=True, tweets=[tweet])
        assert resp.result is True
        assert len(resp.tweets) == 1


class TestUserSchemas:
    def test_user_basic(self):
        user = User(id=1, name="Иван Иванов")
        assert user.id == 1
        assert user.name == "Иван Иванов"

    def test_profile_user_full(self):
        follower = User(id=2, name="Подписчик")
        following = User(id=3, name="Подписка")

        profile = ProfileUser(
            id=1, name="Иван", followers=[follower], following=[following]
        )
        assert len(profile.followers) == 1
        assert profile.following[0].name == "Подписка"

    def test_profile_response(self):
        profile = ProfileUser(id=1, name="Иван", followers=[], following=[])
        resp = ProfileResponse(result=True, user=profile)
        assert resp.result is True
        assert resp.user.id == 1

    def test_from_attributes(self):
        class MockUser:
            id = 1
            name = "Иван Иванов"

        user = User.model_validate(MockUser())
        assert user.id == 1
        assert user.name == "Иван Иванов"

    def test_profile_empty_lists(self):
        profile = ProfileUser(id=1, name="Тест")
        assert profile.followers == []
        assert profile.following == []
