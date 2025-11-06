// Commande personnalisée pour se connecter
Cypress.Commands.add('login', (email, password) => {
    cy.visit('/login')
    cy.get('input[type="email"]').type(email)
    cy.get('input[type="password"]').type(password)
    cy.get('button[type="submit"]').click()
    cy.url().should('eq', 'http://localhost:5173/')
  })
  
  // Commande pour se connecter en tant qu'admin
  Cypress.Commands.add('loginAsAdmin', () => {
    cy.login('admin@padel.com', 'Admin@2025!')
  })
  
  // Commande pour vérifier qu'une route est protégée
  Cypress.Commands.add('checkProtectedRoute', (route) => {
    cy.clearLocalStorage()
    cy.visit(route)
    cy.url().should('include', '/login')
  })