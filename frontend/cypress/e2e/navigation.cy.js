describe('Navigation', () => {
    beforeEach(() => {
      cy.clearLocalStorage()
    })
  
    it('Visiteur ne peut accéder qu\'à l\'accueil', () => {
      cy.visit('/')
      cy.contains('Bienvenue sur Corpo Padel').should('be.visible')
      cy.contains('Se connecter').should('be.visible')
    })
  
    it('Visiteur est redirigé vers login pour les pages protégées', () => {
      cy.visit('/planning')
      cy.url().should('include', '/login')
      
      cy.visit('/matches')
      cy.url().should('include', '/login')
      
      cy.visit('/results')
      cy.url().should('include', '/login')
      
      cy.visit('/profile')
      cy.url().should('include', '/login')
    })
  
    it('Joueur connecté peut naviguer dans l\'application', () => {
      // Se connecter
      cy.visit('/login')
      cy.get('input[type="email"]').type('admin@padel.com')
      cy.get('input[type="password"]').type('Admin@2025!')
      cy.get('button[type="submit"]').click()
      
      // Vérifier que la navbar est visible
      cy.contains('Corpo Padel').should('be.visible')
      cy.contains('Planning').should('be.visible')
      cy.contains('Matchs').should('be.visible')
      cy.contains('Résultats').should('be.visible')
      cy.contains('admin@padel.com').should('be.visible')
    })
  
    it('Navbar affiche le menu admin pour les administrateurs', () => {
      // Se connecter en tant qu'admin
      cy.visit('/login')
      cy.get('input[type="email"]').type('admin@padel.com')
      cy.get('input[type="password"]').type('Admin@2025!')
      cy.get('button[type="submit"]').click()
      
      // Vérifier que le lien Administration est visible
      cy.contains('Administration').should('be.visible')
    })
  })