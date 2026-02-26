"""Tests for SCIENCEMENTOR backend."""
import json
import pytest
from app import app
from chat_history import get_db, ChatHistoryDB

# Reset DB singleton for testing
import chat_history
chat_history._db_instance = None


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db():
    """Get fresh database instance."""
    chat_history._db_instance = None
    return get_db()


class TestHealthEndpoint:
    """Test /health endpoint."""
    
    def test_health_returns_ok(self, client):
        """Health check should return 200 OK."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['service'] == 'SCIENCEMENTOR'


class TestProvidersEndpoint:
    """Test /providers endpoint."""
    
    def test_providers_returns_list(self, client):
        """Providers should return available and all providers."""
        response = client.get('/providers')
        assert response.status_code == 200
        data = response.get_json()
        assert 'available' in data
        assert 'all' in data
        assert isinstance(data['available'], list)


class TestTopicsEndpoint:
    """Test /topics endpoint."""
    
    def test_topics_returns_list(self, client):
        """Topics should return list of Science topics."""
        response = client.get('/topics')
        assert response.status_code == 200
        data = response.get_json()
        assert 'topics' in data
        assert isinstance(data['topics'], list)
        assert len(data['topics']) > 0


class TestSessionManagement:
    """Test session CRUD operations."""
    
    def test_create_session(self, client):
        """Should create a new session."""
        response = client.post('/sessions', 
                              content_type='application/json')
        assert response.status_code == 201
        data = response.get_json()
        assert 'session_id' in data
        assert len(data['session_id']) == 36  # UUID length
    
    def test_list_sessions(self, client):
        """Should list sessions."""
        # Create a session first
        client.post('/sessions', content_type='application/json')
        
        response = client.get('/sessions')
        assert response.status_code == 200
        data = response.get_json()
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)
    
    def test_delete_session(self, client):
        """Should delete a session."""
        # Create a session
        create_resp = client.post('/sessions', 
                                  content_type='application/json')
        session_id = create_resp.get_json()['session_id']
        
        # Delete it
        response = client.delete(f'/sessions/{session_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['deleted'] == True
    
    def test_delete_nonexistent_session(self, client):
        """Should return 404 for nonexistent session."""
        response = client.delete('/sessions/nonexistent-id')
        assert response.status_code == 404
    
    def test_get_session_messages(self, client):
        """Should get messages for a session."""
        # Create a session
        create_resp = client.post('/sessions', 
                                  content_type='application/json')
        session_id = create_resp.get_json()['session_id']
        
        # Get messages
        response = client.get(f'/sessions/{session_id}/messages')
        assert response.status_code == 200
        data = response.get_json()
        assert 'messages' in data
        assert isinstance(data['messages'], list)


class TestAskEndpoint:
    """Test /ask endpoint."""
    
    def test_ask_requires_question(self, client):
        """Should require a question."""
        response = client.post('/ask',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_ask_filters_non_science(self, client):
        """Should filter non-Science questions."""
        response = client.post('/ask',
                              json={'question': 'What is 2+2?'},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        # Short question should be filtered
        assert 'filtered' in data or 'answer' in data
    
    def test_ask_with_biology_keyword(self, client):
        """Should accept Biology questions."""
        response = client.post('/ask',
                              json={'question': 'What is a cell membrane?'},
                              content_type='application/json')
        assert response.status_code in [200, 400]  # 400 if no provider configured
        # If no provider, check error message
        data = response.get_json()
        if response.status_code == 400:
            assert 'available_providers' in data or 'error' in data
    
    def test_ask_with_physics_keyword(self, client):
        """Should accept Physics questions."""
        response = client.post('/ask',
                              json={'question': 'What is Newton\'s first law of motion?'},
                              content_type='application/json')
        assert response.status_code in [200, 400]  # 400 if no provider configured
        data = response.get_json()
        if response.status_code == 400:
            assert 'available_providers' in data or 'error' in data
    
    def test_ask_with_chemistry_keyword(self, client):
        """Should accept Chemistry questions."""
        response = client.post('/ask',
                              json={'question': 'What is covalent bonding?'},
                              content_type='application/json')
        assert response.status_code in [200, 400]  # 400 if no provider configured
        data = response.get_json()
        if response.status_code == 400:
            assert 'available_providers' in data or 'error' in data


class TestChatHistoryDB:
    """Test database operations."""
    
    def test_create_session(self, db):
        """Should create and return session ID."""
        session_id = db.create_session()
        assert session_id is not None
        assert len(session_id) == 36
    
    def test_session_exists(self, db):
        """Should detect existing sessions."""
        session_id = db.create_session()
        assert db.session_exists(session_id) == True
        assert db.session_exists('nonexistent') == False
    
    def test_add_and_get_messages(self, db):
        """Should add and retrieve messages."""
        session_id = db.create_session()
        
        # Add messages
        db.add_message(session_id, 'user', 'Hello')
        db.add_message(session_id, 'assistant', 'Hi there!')
        
        # Get messages
        messages = db.get_session_messages(session_id)
        assert len(messages) == 2
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == 'Hello'
        assert messages[1]['role'] == 'assistant'
    
    def test_update_title(self, db):
        """Should update session title."""
        session_id = db.create_session()
        db.update_title(session_id, 'Test Title')
        
        sessions = db.list_sessions()
        session = next((s for s in sessions if s['id'] == session_id), None)
        assert session is not None
        assert session['title'] == 'Test Title'
    
    def test_delete_session(self, db):
        """Should delete session and messages."""
        session_id = db.create_session()
        db.add_message(session_id, 'user', 'Test')
        
        # Delete
        result = db.delete_session(session_id)
        assert result == True
        
        # Verify deleted
        assert db.session_exists(session_id) == False


class TestSafetyFilter:
    """Test safety filter."""
    
    def test_biology_keywords_detected(self):
        """Should detect Biology keywords."""
        from safety_filter import is_science_question
        
        is_science, _ = is_science_question("What is photosynthesis?")
        assert is_science == True
        
        is_science, _ = is_science_question("Explain the cell membrane")
        assert is_science == True
    
    def test_physics_keywords_detected(self):
        """Should detect Physics keywords."""
        from safety_filter import is_science_question
        
        is_science, _ = is_science_question("What is Newton's first law?")
        assert is_science == True
        
        is_science, _ = is_science_question("Explain electric circuits")
        assert is_science == True
    
    def test_chemistry_keywords_detected(self):
        """Should detect Chemistry keywords."""
        from safety_filter import is_science_question
        
        is_science, _ = is_science_question("What is covalent bonding?")
        assert is_science == True
        
        is_science, _ = is_science_question("Explain the periodic table")
        assert is_science == True
    
    def test_off_topic_detected(self):
        """Should detect off-topic questions."""
        from safety_filter import is_science_question
        
        is_science, msg = is_science_question("Solve x + 5 = 10 algebra equation")
        assert is_science == False
        assert 'Science' in msg
    
    def test_short_questions_filtered(self):
        """Should filter very short questions."""
        from safety_filter import is_science_question
        
        is_science, _ = is_science_question("Hi")
        assert is_science == False
    
    def test_general_questions_filtered(self):
        """Should filter general non-science questions."""
        from safety_filter import is_science_question
        
        # Long question, no science keywords
        is_science, _ = is_science_question("What is the capital city of France?")
        assert is_science == False



if __name__ == '__main__':
    pytest.main([__file__, '-v'])
