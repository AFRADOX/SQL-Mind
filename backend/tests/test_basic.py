# backend/tests/test_basic.py

def test_password_hashing():
    """Test that passwords are hashed correctly"""
    from app.core.security import hash_password, verify_password
    
    plain = "Test1234"
    hashed = hash_password(plain)
    
    # hashed should not equal plain
    assert hashed != plain
    # verify should return True
    assert verify_password(plain, hashed) == True
    # wrong password should return False
    assert verify_password("wrongpass", hashed) == False


def test_sql_validation_blocks_delete():
    """Test that DELETE statements are blocked"""
    from app.services.validation_service import ValidationService
    from app.core.exceptions import UnsafeSQLException
    import pytest
    
    validator = ValidationService()
    
    try:
        validator.validate("DELETE FROM users")
        assert False, "Should have raised exception"
    except UnsafeSQLException:
        assert True


def test_sql_validation_allows_select():
    """Test that SELECT statements are allowed"""
    from app.services.validation_service import ValidationService
    
    validator = ValidationService()
    result = validator.validate("SELECT * FROM users")
    
    assert result == "SELECT * FROM users"


def test_confidence_scoring():
    """Test confidence scoring returns correct levels"""
    from app.services.confidence_service import ConfidenceService
    from app.schemas.schema import DatabaseSchema, TableMeta, ColumnMeta
    
    service = ConfidenceService()
    
    # Create a simple mock schema
    schema = DatabaseSchema(
        tables=[
            TableMeta(
                name="users",
                columns=[
                    ColumnMeta(name="id", type="INTEGER", nullable=False, is_primary_key=True),
                    ColumnMeta(name="email", type="VARCHAR", nullable=False, is_primary_key=False),
                ],
                foreign_keys=[],
                sample_values={}
            )
        ],
        total_tables=1
    )
    
    result = service.score(90, "SELECT * FROM users LIMIT 10", schema)
    
    assert result["score"] > 0
    assert result["level"] in ["HIGH", "MEDIUM", "LOW"]
    assert "breakdown" in result