-- ============================================================================
-- Script d'initialisation des données de test Oracle
-- Exécuter avec : sqlplus system/OraclePassword123@localhost:1521/XEPDB1
-- ============================================================================

-- Créer un utilisateur de test
CREATE USER testuser IDENTIFIED BY TestPass123
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

-- Accorder des privilèges
GRANT CONNECT, RESOURCE TO testuser;
GRANT CREATE SESSION TO testuser;

-- Créer des tables de test
CREATE TABLE testuser.employees (
    employee_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(50),
    last_name VARCHAR2(50),
    email VARCHAR2(100),
    department_id NUMBER,
    salary NUMBER(10,2),
    hire_date DATE
);

CREATE TABLE testuser.departments (
    department_id NUMBER PRIMARY KEY,
    department_name VARCHAR2(100),
    manager_id NUMBER
);

-- Insérer des données
INSERT INTO testuser.departments VALUES (10, 'IT', 1);
INSERT INTO testuser.departments VALUES (20, 'Sales', 2);
INSERT INTO testuser.departments VALUES (30, 'HR', 3);

INSERT INTO testuser.employees VALUES (1, 'John', 'Doe', 'john.doe@company.com', 10, 75000, SYSDATE-1000);
INSERT INTO testuser.employees VALUES (2, 'Jane', 'Smith', 'jane.smith@company.com', 20, 65000, SYSDATE-800);
INSERT INTO testuser.employees VALUES (3, 'Bob', 'Johnson', 'bob.j@company.com', 10, 80000, SYSDATE-600);
INSERT INTO testuser.employees VALUES (4, 'Alice', 'Williams', 'alice.w@company.com', 30, 70000, SYSDATE-400);
INSERT INTO testuser.employees VALUES (5, 'Charlie', 'Brown', 'charlie.b@company.com', 20, 68000, SYSDATE-200);

COMMIT;

-- Activer l'audit
AUDIT SELECT, INSERT, UPDATE, DELETE ON testuser.employees BY ACCESS;
AUDIT SELECT, INSERT, UPDATE, DELETE ON testuser.departments BY ACCESS;

-- Créer quelques requêtes lentes pour les tests
BEGIN
    FOR i IN 1..100 LOOP
        EXECUTE IMMEDIATE 'SELECT * FROM testuser.employees WHERE employee_id = ' || MOD(i, 5) + 1;
    END LOOP;
END;
/

SELECT 'Setup terminé !' FROM DUAL;