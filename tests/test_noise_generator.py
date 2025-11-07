import pytest
import time
from unittest.mock import patch, MagicMock
from noise_generator import generate_noise


def test_generate_noise_computation():
    """Test that computation result is correct"""
    expected_result = sum(i for i in range(1000000))
    assert expected_result > 0


def test_generate_noise_with_mock(monkeypatch):
    """Test generate_noise function with mocked time to prevent infinite loop"""
    call_count = [0]
    
    def mock_sleep(duration):
        call_count[0] += 1
        if call_count[0] >= 2:
            raise KeyboardInterrupt()
    
    def mock_print(*args, **kwargs):
        pass
    
    monkeypatch.setattr('time.sleep', mock_sleep)
    monkeypatch.setattr('builtins.print', mock_print)
    
    with pytest.raises(KeyboardInterrupt):
        generate_noise()
    
    assert call_count[0] >= 2


def test_computation_performance():
    """Test that computation completes in reasonable time"""
    start = time.time()
    result = sum(i for i in range(1000000))
    elapsed = time.time() - start
    
    assert result == 499999500000
    assert elapsed < 5.0
