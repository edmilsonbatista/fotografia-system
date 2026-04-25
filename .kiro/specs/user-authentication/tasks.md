# Implementation Plan: User Authentication

## Overview

Add session-based authentication to Photo Pro Studio using Flask-Login. All auth code integrates into the existing single-file `app.py` architecture. The implementation follows an incremental approach: model first, then CLI setup, login page, route protection, and finally navbar integration.

## Tasks

- [x] 1. Install dependencies and configure Flask-Login
  - [x] 1.1 Add `flask-login` to `requirements.txt` and install it
    - Add `Flask-Login` to `requirements.txt`
    - _Requirements: 6.1_

  - [x] 1.2 Configure SECRET_KEY and LoginManager in `app.py`
    - Replace the hardcoded `SECRET_KEY` with `os.environ.get('SECRET_KEY', os.urandom(24))`
    - Import `LoginManager` from `flask_login` and initialize it on the app
    - Set `login_manager.login_view = 'login'`
    - Set `login_manager.login_message = 'Por favor, faça login para acessar o sistema.'`
    - Set `login_manager.login_message_category = 'info'`
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

- [x] 2. Implement Usuario model and user_loader
  - [x] 2.1 Create the `Usuario` SQLAlchemy model in `app.py`
    - Import `UserMixin` from `flask_login` and `generate_password_hash`, `check_password_hash` from `werkzeug.security`
    - Define `Usuario(UserMixin, db.Model)` with columns: `id` (Integer, PK), `username` (String(80), unique, not null), `password_hash` (String(256), not null)
    - Implement `set_password(self, password)` using `generate_password_hash`
    - Implement `check_password(self, password)` using `check_password_hash`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 2.2 Register the `user_loader` callback
    - Add `@login_manager.user_loader` that queries `Usuario` by ID
    - Return `None` for non-existent IDs
    - _Requirements: 6.2_

  - [ ]\* 2.3 Write property test: password hash round-trip
    - **Property 1: Password hash round-trip**
    - Use Hypothesis to generate arbitrary password strings
    - Assert `set_password(pw)` then `check_password(pw)` returns `True`
    - Assert `check_password(other_pw)` returns `False` when `other_pw != pw`
    - **Validates: Requirements 1.3, 1.4**

  - [ ]\* 2.4 Write property test: user_loader correctness
    - **Property 9: user_loader returns correct user by ID**
    - Use Hypothesis to generate users, verify `load_user(id)` returns the correct `Usuario`
    - Verify `load_user(non_existent_id)` returns `None`
    - **Validates: Requirements 6.2**

  - [ ]\* 2.5 Write unit tests for Usuario model
    - Test column types and constraints (username unique, max lengths)
    - Test `UserMixin` interface: `is_authenticated`, `is_active`, `is_anonymous`, `get_id`
    - _Requirements: 1.1, 1.2, 1.5_

- [x] 3. Implement CLI `create-admin` command and default admin
  - [x] 3.1 Add the `create-admin` CLI command in `app.py`
    - Import `click` and register `@app.cli.command('create-admin')` with `--username` and `--password` options
    - Create a `Usuario` with hashed password if username doesn't exist
    - Print "Usuário admin criado com sucesso!" on success
    - Print "Usuário já existe!" and abort if username is taken
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.2 Add default admin auto-creation after `db.create_all()`
    - After `db.create_all()`, check if any `Usuario` exists
    - If none, create a user with username `"admin"` and password `"admin"` (hashed)
    - _Requirements: 2.5_

  - [ ]\* 3.3 Write property test: CLI creates hashed user
    - **Property 2: CLI create-admin produces hashed user**
    - Use Hypothesis to generate username/password pairs
    - Invoke CLI runner with `create-admin`, verify `password_hash != plaintext` and `check_password` returns `True`
    - **Validates: Requirements 2.2**

  - [ ]\* 3.4 Write property test: CLI rejects duplicate username
    - **Property 3: CLI create-admin rejects duplicate username**
    - Create a user, then invoke `create-admin` with the same username
    - Verify error message and that the original `password_hash` is unchanged
    - **Validates: Requirements 2.3**

  - [ ]\* 3.5 Write unit tests for CLI and default admin
    - Test `create-admin` command is registered
    - Test success confirmation message output
    - Test default admin/admin is created on empty DB
    - _Requirements: 2.1, 2.4, 2.5_

- [ ] 4. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement login page and authentication flow
  - [x] 5.1 Create `templates/login.html`
    - Standalone page (no `base.html` extension, no navbar)
    - Include Bootstrap 5.3.2 CSS, Font Awesome 6.5.1, and custom `style.css`
    - Centered card with gradient header (`linear-gradient(135deg, #667eea, #764ba2)`)
    - Display Photo Pro Studio logo above the form
    - Form fields: "Usuário" input, "Senha" input, "Lembrar-me" checkbox, "Entrar" submit button
    - Display flash messages for errors
    - _Requirements: 3.1, 3.2, 3.3, 3.6, 7.3_

  - [x] 5.2 Add `/login` route in `app.py`
    - Handle GET (render login page) and POST (validate credentials)
    - On valid credentials: call `login_user(user, remember=remember_me)` and redirect to `next` URL or dashboard
    - Validate `next` URL is relative (prevent open redirect), fallback to dashboard
    - On invalid credentials: flash "Usuário ou senha inválidos." and re-render login page
    - Wrap DB access in try/except for error handling
    - _Requirements: 3.4, 3.5, 3.7, 4.3_

  - [ ]\* 5.3 Write property test: valid credentials authenticate
    - **Property 4: Valid credentials produce authenticated session**
    - Use Hypothesis to generate user/password, submit to login, verify redirect and authenticated session
    - **Validates: Requirements 3.4**

  - [ ]\* 5.4 Write property test: invalid credentials rejected
    - **Property 5: Invalid credentials are rejected**
    - Use Hypothesis to generate wrong username or wrong password attempts
    - Verify no session created and login page returned with error flash
    - **Validates: Requirements 3.5**

  - [ ]\* 5.5 Write unit tests for login page
    - Test login page renders form elements (Usuário, Senha, Lembrar-me, Entrar)
    - Test gradient header and logo presence
    - Test remember-me sets persistent session
    - Test login page has no navbar
    - _Requirements: 3.1, 3.2, 3.3, 3.6, 3.7, 7.3_

- [x] 6. Protect all routes and add logout
  - [x] 6.1 Add `@login_required` to all existing routes in `app.py`
    - Import `login_required` from `flask_login`
    - Decorate all existing route functions (dashboard, listar_eventos, novo_evento, caixa, importar, all API routes, etc.)
    - Do NOT decorate the `/login` route
    - _Requirements: 4.1, 4.2, 4.4_

  - [x] 6.2 Add custom unauthorized handler for API routes
    - Register `@login_manager.unauthorized_handler`
    - If request path starts with `/api/`, return JSON `{"error": "Autenticação necessária."}` with HTTP 401
    - Otherwise, redirect to login page (default Flask-Login behavior with `next` parameter)
    - _Requirements: 4.2, 4.3, 4.5_

  - [x] 6.3 Add `/logout` route in `app.py`
    - Import `logout_user` from `flask_login`
    - Call `logout_user()` and redirect to login page
    - Decorate with `@login_required`
    - _Requirements: 5.1, 5.2_

  - [ ]\* 6.4 Write property test: protected routes redirect
    - **Property 6: Protected routes redirect unauthenticated users**
    - Use Hypothesis to pick from known protected route paths
    - Verify unauthenticated GET returns redirect to `/login`
    - **Validates: Requirements 4.1, 4.2**

  - [ ]\* 6.5 Write property test: next URL preservation
    - **Property 7: Next URL preservation through login flow**
    - Use Hypothesis to generate protected route URLs
    - Verify redirect includes `next` parameter, and after login the user lands on the original URL
    - **Validates: Requirements 4.3**

  - [ ]\* 6.6 Write property test: API routes return 401
    - **Property 8: API routes return 401 for unauthenticated requests**
    - Use Hypothesis to pick from known API route paths
    - Verify unauthenticated request returns HTTP 401 with JSON error
    - **Validates: Requirements 4.4, 4.5**

  - [ ]\* 6.7 Write unit tests for logout and route protection
    - Test logout terminates session and redirects to login
    - Test SECRET_KEY is not the hardcoded placeholder
    - Test LoginManager configuration values
    - _Requirements: 5.1, 5.2, 6.3, 6.4, 6.5_

- [x] 7. Update navbar for authentication state
  - [x] 7.1 Modify `templates/base.html` navbar
    - Add conditional block: if `current_user.is_authenticated`, show username and "Sair" link with `fa-sign-out-alt` icon
    - "Sair" link points to `{{ url_for('logout') }}`
    - Import `current_user` from `flask_login` (already available in Jinja context via Flask-Login)
    - _Requirements: 5.3, 5.4, 7.1, 7.2_

  - [ ]\* 7.2 Write unit tests for navbar authentication state
    - Test navbar shows username when authenticated
    - Test navbar shows "Sair" link when authenticated
    - _Requirements: 7.1, 7.2_

- [ ] 8. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- All code changes are in `app.py`, `templates/base.html`, and the new `templates/login.html` — matching the project's single-file architecture
- Property tests use Hypothesis with pytest; each test runs 100+ iterations against an in-memory SQLite database
- The implementation language is Python, matching the existing codebase
