describe('Authentification', () => {
  beforeEach(() => {
    // Nettoyer le localStorage
    cy.clearLocalStorage()
    cy.visit('http://localhost:5173')
  })

  it('Affiche la page de login', () => {
    cy.visit('/login')
    cy.contains('Corpo Padel').should('be.visible')
    cy.contains('Connectez-vous à votre compte').should('be.visible')
    cy.get('input[type="email"]').should('be.visible')
    cy.get('input[type="password"]').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
  })

  it('Connexion réussie avec credentials valides', () => {
    cy.visit('/login')
    
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Vérifier la redirection vers la page d'accueil
    cy.url().should('eq', 'http://localhost:5173/')
    cy.contains('Bonjour').should('be.visible')
    cy.contains('admin@padel.com').should('be.visible')
  })

  it('Connexion échoue avec email invalide', () => {
    cy.visit('/login')
    
    cy.get('input[type="email"]').type('wrong@example.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Vérifier le message d'erreur
    cy.contains('Email ou mot de passe incorrect').should('be.visible')
    cy.contains('Tentatives restantes').should('be.visible')
  })

  it('Connexion échoue avec mot de passe invalide', () => {
    cy.visit('/login')
    
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('WrongPassword')
    cy.get('button[type="submit"]').click()
    
    // Vérifier le message d'erreur
    cy.contains('Email ou mot de passe incorrect').should('be.visible')
  })

  it('Bloque le compte après 5 tentatives échouées', () => {
    cy.visit('/login')
    
    // Faire 5 tentatives échouées
    for (let i = 0; i < 5; i++) {
      cy.get('input[type="email"]').clear().type('admin@padel.com')
      cy.get('input[type="password"]').clear().type('WrongPassword')
      cy.get('button[type="submit"]').click()
      cy.wait(500)
    }
    
    // Vérifier le message de blocage
    cy.contains('Compte bloqué').should('be.visible')
    cy.contains('minutes').should('be.visible')
    cy.get('button[type="submit"]').should('be.disabled')
  })

  it('Redirection automatique si déjà connecté', () => {
    // Se connecter d'abord
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Attendre la redirection
    cy.url().should('eq', 'http://localhost:5173/')
    
    // Essayer d'accéder à /login
    cy.visit('/login')
    
    // Devrait être redirigé vers l'accueil
    cy.url().should('eq', 'http://localhost:5173/')
  })

  it('Déconnexion fonctionne correctement', () => {
    // Se connecter
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Vérifier que l'utilisateur est connecté
    cy.url().should('eq', 'http://localhost:5173/')
    
    // Se déconnecter
    cy.contains('Déconnexion').click()
    
    // Vérifier la redirection vers login
    cy.url().should('include', '/login')
    
    // Vérifier que le token est supprimé
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.be.null
    })
  })
})
