import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.profile_service import ProfileService
from app.models.models import User, Player

# --- FIXTURES (Données simulées) ---

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def mock_user():
    user = User(id=1, email="test@example.com", password_hash="hashed_old")
    user.must_change_password = True
    return user

@pytest.fixture
def mock_player():
    return Player(id=1, user_id=1, first_name="Jean", last_name="Dupont", photo_url="old_url")

# --- TESTS ---

def test_get_full_profile(db_session, mock_user, mock_player):
    db_session.query().filter().first.return_value = mock_player
    user, player = ProfileService.get_full_profile(db_session, mock_user)
    assert user.id == 1
    assert player.first_name == "Jean"

def test_update_user_profile_email_taken(db_session, mock_user):
    # Simuler qu'un autre utilisateur existe avec cet email
    db_session.query().filter().filter().first.return_value = User(id=99)
    
    class Data:
        email = "pris@test.com"
        
    with pytest.raises(HTTPException) as exc:
        ProfileService.update_user_profile(db_session, mock_user, Data())
    assert exc.value.status_code == 400

@patch("app.services.profile_service.verify_password")
@patch("app.services.profile_service.get_password_hash")
def test_update_password_success(mock_hash, mock_verify, db_session, mock_user):
    mock_verify.side_effect = [True, False] # Ancien OK, Nouveau différent
    mock_hash.return_value = "new_hash"

    class PwdData:
        current_password = "old"
        new_password = "new"
        confirm_password = "new"

    ProfileService.update_password(db_session, mock_user, PwdData())
    assert mock_user.password_hash == "new_hash"
    db_session.commit.assert_called()

# --- TEST PHOTO (SANS ASYNCIO PLUGIN) ---

def test_handle_photo_upload_base64(db_session, mock_user, mock_player):
    db_session.query().filter().first.return_value = mock_player
    new_photo = "data:image/png;base64,123"

    # Puisque handle_photo_upload est 'async def', elle renvoie une coroutine.
    # On utilise .send(None) pour l'exécuter jusqu'au bout sans boucle d'événement.
    coro = ProfileService.handle_photo_upload(db_session, mock_user, new_photo)
    try:
        coro.send(None)
    except StopIteration as e:
        result = e.value # On récupère le return de la fonction

    assert result["photo_url"] == new_photo
    assert mock_player.photo_url == new_photo
    db_session.commit.assert_called()

def test_handle_photo_delete_success(db_session, mock_user, mock_player):
    db_session.query().filter().first.return_value = mock_player
    ProfileService.handle_photo_delete(db_session, mock_user)
    assert mock_player.photo_url is None
    db_session.commit.assert_called()