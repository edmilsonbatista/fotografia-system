# Requirements Document

## Introduction

Photo Pro Studio is a Flask-based photography studio management system that currently has no authentication mechanism. Any user who accesses the application URL can view and modify all financial data, events, and transactions. This feature adds a session-based login system using Flask-Login to protect all application routes, ensuring only the authenticated photographer (single-user system) can access the system. The login page must match the existing visual style with gradients and modern Bootstrap 5 design. All UI elements are in Brazilian Portuguese.

## Glossary

- **Auth_System**: The authentication module responsible for managing user login, logout, session handling, and route protection within Photo Pro Studio.
- **User_Model**: The SQLAlchemy database model representing the single administrator user, storing username and hashed password.
- **Login_Page**: The web page presented to unauthenticated visitors, containing the login form with username and password fields.
- **Session**: A server-side Flask session that tracks whether a user is currently authenticated.
- **Protected_Route**: Any application route that requires an active authenticated Session before granting access.
- **Remember_Me**: An optional login feature that persists the authentication Session across browser restarts using a persistent cookie.
- **CLI_Command**: A Flask command-line interface command executed via `flask` in the terminal to perform administrative tasks such as creating the initial user.

## Requirements

### Requirement 1: User Model and Password Storage

**User Story:** As the photographer, I want my credentials stored securely in the database, so that my password cannot be read even if the database file is accessed.

#### Acceptance Criteria

1. THE User_Model SHALL store a username field as a unique, non-nullable string with a maximum length of 80 characters.
2. THE User_Model SHALL store a password_hash field as a non-nullable string with a maximum length of 256 characters.
3. WHEN a password is set on the User_Model, THE Auth_System SHALL hash the password using werkzeug.security.generate_password_hash before storing the value in password_hash.
4. THE User_Model SHALL provide a method to verify a plaintext password against the stored password_hash using werkzeug.security.check_password_hash.
5. THE User_Model SHALL implement the Flask-Login UserMixin interface to provide is_authenticated, is_active, is_anonymous, and get_id properties.

### Requirement 2: Initial User Creation via CLI

**User Story:** As the photographer, I want to create my admin account through a command-line tool, so that I can set up authentication without needing a public registration page.

#### Acceptance Criteria

1. THE Auth_System SHALL provide a CLI_Command named `create-admin` registered with the Flask application.
2. WHEN the `create-admin` CLI_Command is executed with a username and password, THE Auth_System SHALL create a new User_Model record with the hashed password in the database.
3. IF a User_Model record with the provided username already exists, THEN THE Auth_System SHALL display an error message "Usuário já existe!" and abort the operation without modifying the existing record.
4. WHEN the `create-admin` CLI_Command completes successfully, THE Auth_System SHALL display a confirmation message "Usuário admin criado com sucesso!".
5. IF no User_Model record exists when the application starts, THEN THE Auth_System SHALL create a default admin user with username "admin" and password "admin" during database initialization.

### Requirement 3: Login Page and Authentication Flow

**User Story:** As the photographer, I want a login page that matches the application's visual style, so that I can securely access my studio management system.

#### Acceptance Criteria

1. THE Login_Page SHALL display a centered card with a gradient header matching the application's existing bg-primary gradient style (linear-gradient 135deg, #667eea to #764ba2).
2. THE Login_Page SHALL contain a username input field with the label "Usuário", a password input field with the label "Senha", a Remember_Me checkbox with the label "Lembrar-me", and a submit button with the text "Entrar".
3. THE Login_Page SHALL display the Photo Pro Studio logo above the login form.
4. WHEN a user submits valid credentials on the Login_Page, THE Auth_System SHALL create an authenticated Session and redirect the user to the dashboard page.
5. WHEN a user submits invalid credentials on the Login_Page, THE Auth_System SHALL display a flash message "Usuário ou senha inválidos." and remain on the Login_Page.
6. THE Login_Page SHALL use the existing Bootstrap 5.3.2 framework, Font Awesome 6.5.1 icons, and the application's custom CSS styles.
7. WHEN the Remember_Me checkbox is selected during login, THE Auth_System SHALL configure the Session to persist across browser restarts.

### Requirement 4: Route Protection

**User Story:** As the photographer, I want all application pages protected behind authentication, so that unauthorized users cannot access my financial data and event information.

#### Acceptance Criteria

1. THE Auth_System SHALL protect all existing application routes by requiring an active authenticated Session before granting access.
2. WHEN an unauthenticated user attempts to access any Protected_Route, THE Auth_System SHALL redirect the user to the Login_Page.
3. WHEN an unauthenticated user is redirected to the Login_Page, THE Auth_System SHALL preserve the originally requested URL so that after successful login the user is redirected to the intended page.
4. THE Auth_System SHALL protect all API routes (paths starting with `/api/`) by requiring an active authenticated Session.
5. WHEN an unauthenticated request is made to an API route, THE Auth_System SHALL return an HTTP 401 status code with a JSON response containing an error message.

### Requirement 5: Logout Functionality

**User Story:** As the photographer, I want to log out of the system, so that I can prevent unauthorized access when I leave my computer.

#### Acceptance Criteria

1. THE Auth_System SHALL provide a logout route accessible at the `/logout` URL path.
2. WHEN the logout route is accessed, THE Auth_System SHALL terminate the current authenticated Session and redirect the user to the Login_Page.
3. THE Auth_System SHALL display a "Sair" link with a sign-out icon in the application navigation bar, visible only to authenticated users.
4. WHEN the user clicks the "Sair" link, THE Auth_System SHALL invoke the logout route.

### Requirement 6: Flask-Login Integration

**User Story:** As the photographer, I want session management handled by a proven library, so that authentication is reliable and secure.

#### Acceptance Criteria

1. THE Auth_System SHALL use the Flask-Login extension for session management and user loading.
2. THE Auth_System SHALL configure a user_loader callback that retrieves the User_Model from the database by user ID.
3. THE Auth_System SHALL set the login_view configuration to redirect unauthenticated users to the Login_Page.
4. THE Auth_System SHALL set the login_message to "Por favor, faça login para acessar o sistema." displayed as an informational flash message.
5. THE Auth_System SHALL configure the application SECRET_KEY with a cryptographically secure value instead of the current hardcoded placeholder string.

### Requirement 7: Navigation Bar Authentication State

**User Story:** As the photographer, I want the navigation bar to reflect my login state, so that I can see my identity and access the logout option.

#### Acceptance Criteria

1. WHILE a user is authenticated, THE Auth_System SHALL display the username in the navigation bar.
2. WHILE a user is authenticated, THE Auth_System SHALL display the "Sair" logout link in the navigation bar.
3. THE Login_Page SHALL render without the application navigation bar, displaying only the login form.
