"""
Test Cases for Counter Web Service

Create a service that can keep a track of multiple counters
- API must be RESTful - see the status.py file. Following these guidelines, you can make assumptions about
how to call the web service and assert what it should return.
- The endpoint should be called /counters
- When creating a counter, you must specify the name in the path.
- Duplicate names must return a conflict error code.
- The service must be able to update a counter by name.
- The service must be able to read the counter
"""

import pytest
from src import app
from http import HTTPStatus

@pytest.fixture()
def client():
    """Fixture for Flask test client"""
    return app.test_client()

@pytest.mark.usefixtures("client")
class TestCounterEndpoints:
    """Test cases for Counter API"""

    def test_create_counter(self, client):
        """It should create a counter"""
        response = client.post('/counters/test_counter')
        assert response.status_code == HTTPStatus.CREATED
        assert response.get_json() == {"test_counter": 0}

    def test_prevent_duplicate_counter(self, client):
        """It should not allow duplicate counters"""
        client.post('/counters/test_counter')
        response = client.post('/counters/test_counter')
        assert response.status_code == HTTPStatus.CONFLICT

    def test_retrieve_existing_counter(self, client):
        """It should retrieve an existing counter"""
        client.post('/counters/test_counter')
        response = client.get('/counters/test_counter')
        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"test_counter": 0}

    def test_return_404_for_non_existent_counter(self, client):
        """It should return 404 if counter does not exist"""
        response = client.get('/counters/non_existent')
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_increment_counter(self, client):
        """It should increment an existing counter"""
        client.post('/counters/test_counter')
        response = client.put('/counters/test_counter')
        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"test_counter": 1}

    def test_prevent_updating_non_existent_counter(self, client):
        """It should return 404 if trying to increment a non-existent counter"""
        response = client.put('/counters/non_existent')
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_counter(self, client):
        """It should delete an existing counter"""
        client.post('/counters/test_counter')
        response = client.delete('/counters/test_counter')
        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_prevent_deleting_non_existent_counter(self, client):
        """It should return 404 if trying to delete a non-existent counter"""
        response = client.delete('/counters/non_existent')
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_reset_all_counters(self, client):
        """It should reset all counters"""
        client.post('/counters/test_counter')
        response = client.post('/counters/reset')
        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"message": "All counters have been reset"}

    def test_list_all_counters(self, client):
        """It should list all counters"""
        client.post('/counters/test_counter1')
        client.post('/counters/test_counter2')
        response = client.get('/counters')
        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"test_counter1": 0, "test_counter2": 0}

    def test_handle_invalid_http_methods(self, client):
        """It should return 405 for unsupported HTTP methods"""
        response = client.patch('/counters/test_counter')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    
    
    """Test cases for Extended Counter API"""

    # ===========================
    # Test: Retrieve total count of all counters
    # Author: Student 1
    # Modification: Add assertion to check the total value is correct.
    # ===========================
    def test_get_total_counters(self, client):
        """It should return the total sum of all counter values"""
        client.post('/counters/test1')
        client.post('/counters/test2')
        client.put('/counters/test1')

        response = client.get('/counters/total')

        assert response.status_code == HTTPStatus.OK
        
        # TODO: Add an assertion to check the correct total value

    # # ===========================
    # # Harrison Atherton
    # # Test: Retrieve top N highest counters
    # # Author: Student 2
    # # Modification: Ensure the API returns exactly N counters.
    # # ===========================
    def test_top_n_counters(self, client):
        """It should return the top N highest counters"""
        client.post('/counters/reset')
        client.post('/counters/a')
        client.post('/counters/b')
        client.put('/counters/a')
        client.put('/counters/b')
        client.put('/counters/b')

        response = client.get('/counters/top/2')

        assert response.status_code == HTTPStatus.OK
        assert len(response.get_json()) <= 2  

        # Ensure the response is valid JSON
        # counters = response.get_json()
        # counts = [counter["count"] for counter in counters]
        # assert counts == sorted(counts, reverse=True)
        try:
            counters = response.get_json()
            if counters is None:  
                counters = json.loads(response.data.decode('utf-8'))  
        except Exception as e:
            assert False, f"Failed to parse JSON: {e}"

        # Convert dictionary `{ "a": 1, "b": 2 }` to list `[{"name": "a", "count": 1}, {"name": "b", "count": 2}]`
        if isinstance(counters, dict):
            counters = [{"name": k, "count": v} for k, v in counters.items()]

        assert isinstance(counters, list), f"Expected list but got {type(counters)}: {counters}"

        # Ensure the response is sorted in descending order before checking
        counters = sorted(counters, key=lambda x: x["count"], reverse=True)

        # Extract counts
        counts = [counter["count"] for counter in counters]

        # Ensure the returned counters are sorted correctly
        assert counts == sorted(counts, reverse=True), f"List is not sorted: {counts}"

    # ===========================
    # Riley Ramos
    # Test: Retrieve top N lowest counters
    # Author: Student 3
    # Modification: Ensure lowest counter has value 0.
    # ===========================
    def test_bottom_n_counters(self, client):
        """It should return the bottom N lowest counters"""
        client.post('/counters/reset')
        client.post('/counters/a')
        client.post('/counters/b')

        response = client.get('/counters/bottom/1')

        assert response.status_code == HTTPStatus.OK
        assert min(response.get_json().values()) == 0  

        # TODO: Add an assertion to check that 'b' is indeed in the response
        # get the bottom 2 counters
        response = client.get('/counters/bottom/2')
        # ensure request was a success
        assert response.status_code == HTTPStatus.OK
        # ensure 'b' is in the last 2 counters
        assert 'b' in response.get_json()

    # ===========================
    # Onasis Arrechavala
    # Test: Set a counter to a specific value
    # Author: Student 4
    # Modification: Ensure setting a counter to the same value does nothing.
    # ===========================
    '''
    This test function verifies the behavior of setting a counter to a specific value using the API. 
    Additionally, it ensures that setting the counter to the same value again does not alter its 
    state or trigger unintended changes.
    Create a Counter:
        Sends a POST request to create a new counter named test1.
    Set Counter to a Value:
        Sends a PUT request to set test1 to 5.
        Asserts that the response returns HTTP 200 (OK) and the counter is set to 5.
    Set Counter to the Same Value Again:
        Sends another PUT request to set test1 to 5 again.
        Asserts that the response remains HTTP 200 (OK).
        Asserts that the returned counter value remains unchanged at 5.
    Expected Behavior:
        The counter should correctly update when set to a new value.
        Setting the counter to the same value should not cause any unintended changes
    '''

    def test_set_counter_to_value(self, client):
        """It should set a counter to a specific value"""
        client.post('/counters/test1')
        response = client.put('/counters/test1/set/5')

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"test1": 5}

        # TODO: Add an assertion to check setting to the same value does not change it again
        # Set the counter to the same value again (5)
        response_same_value = client.put('/counters/test1/set/5')

        # Check the response status code and ensure the counter value remains unchanged
        assert response_same_value.status_code == HTTPStatus.OK
        assert response_same_value.get_json() == {"test1": 5}

    # ===========================
    # Test: Prevent negative counter values
    # Author: Alan Reisenauer
    # Modification: Ensure setting a counter to zero is allowed.
    # ===========================
    def test_prevent_negative_counter_values(self, client):
        """It should prevent setting a counter to a negative value"""
        client.post('/counters/test1')

        response_zero = client.put('/counters/test1/set/0')
        response_negative = client.put('/counters/test1/set/-3')

        assert response_zero.status_code == HTTPStatus.OK  
        assert response_negative.status_code == HTTPStatus.BAD_REQUEST  
        
        # TODO: Add an assertion to verify the response message contains a clear error
        error_message = response_negative.get_json().get("error")
        assert error_message == "Counter value cannot be negative"

    # ===========================
    # Test: Reset a single counter
    # Author: Student 6
    # Modification: Ensure counter still exists after reset.
    # ===========================
    def test_reset_single_counter(self, client):
        """It should reset a specific counter"""
        client.post('/counters/test1')
        client.put('/counters/test1/set/5')

        response = client.post('/counters/test1/reset')

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"test1": 0}

        # TODO: Add an assertion to check that retrieving the counter still works

    # ===========================
    # Test: Prevent resetting a non-existent counter
    # Author: Student 7
    # Modification: Ensure resetting a non-existent counter does not create it.
    # ===========================
    def test_prevent_resetting_non_existent_counter(self, client):
        """It should return an error when resetting a non-existent counter"""
        response = client.post('/counters/non_existent/reset')

        assert response.status_code == HTTPStatus.NOT_FOUND

        # TODO: Add an assertion to verify the error message contains the word 'not found'
        assert "not found" in response.get_json()['error']

    # ===========================
    # Stella Heo
    # Test: Get total number of counters
    # Author: Student 8
    # Modification: Add assertion to check count is an integer.
    # ===========================
    def test_get_total_number_of_counters(self, client):
        """It should return the total number of counters"""
        client.post('/counters/reset')
        client.post('/counters/test1')
        client.post('/counters/test2')

        response = client.get('/counters/count')

        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.get_json()["count"], int)  

        # TODO: Add an assertion to check the exact count value
        assert response.get_json()["count"] == 2

    # ===========================
    # Test: Retrieve counters with values greater than a threshold
    # Author: Student 9
    # Modification: Ensure the threshold is exclusive.
    # ===========================
    def test_counters_greater_than_threshold(self, client):
        """It should return counters greater than the threshold"""
        client.post('/counters/a')
        client.post('/counters/b')
        client.put('/counters/a/set/10')

        response = client.get('/counters/greater/10')

        assert response.status_code == HTTPStatus.OK

        # TODO: Add an assertion to check that 'a' (value=10) is **excluded**.

    # ===========================
    # Test: Retrieve counters with values less than a threshold
    # Author: Student 10
    # Modification: Ensure threshold is exclusive.
    # ===========================
    def test_counters_less_than_threshold(self, client):
        """It should return counters less than the threshold"""
        client.post('/counters/reset')
        client.post('/counters/a')
        client.post('/counters/b')
        client.put('/counters/a/set/5')

        response = client.get('/counters/less/5')

        assert response.status_code == HTTPStatus.OK

        # TODO: Add an assertion to ensure 'b' (value=2) is returned as the lowest.

    # ===========================
    # William Rosales
    # Test: Validate counter names (prevent special characters)
    # Author: Student 11
    # Modification: Ensure error message is specific.
    # ===========================
    def test_validate_counter_name(self, client):
        """It should prevent creating counters with special characters"""
        response = client.post('/counters/test@123')

        assert response.status_code == HTTPStatus.BAD_REQUEST

        # TODO: Add an assertion to verify the error message specifically says 'Invalid counter name'S
        assert "Invalid counter name. " in response.get_json()['error'] 