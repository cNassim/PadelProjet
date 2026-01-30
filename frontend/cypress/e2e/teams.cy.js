describe('Gestion des Équipes', () => {
  const COMPANY_NAME = 'Cypress Corp' 

  beforeEach(() => {
    cy.viewport(1280, 720)
    cy.visit('http://localhost:5173/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    cy.url().should('not.include', '/login')
    cy.wait(1000)
  })

  it('Cycle complet avec nettoyage intelligent', () => {
    cy.intercept('POST', '**/teams/').as('createTeam')

    // --- 1. NETTOYAGE UNIVERSEL ---
    cy.visit('http://localhost:5173/teams')
    cy.wait(500)
    
    // Fonction récursive pour supprimer TOUT ce qui contient "Cypress"
    // (Que ce soit "Cypress Corp" ou "Team Cypress 123456"...)
    const cleanAllCypressTeams = () => {
      cy.get('body').then(($body) => {
        // On cherche globalement le mot "Cypress" dans le tableau
        if ($body.find('table').text().includes('Cypress')) {
          cy.log('🧹 Nettoyage : Une équipe Cypress traîne encore...')
          
          // On trouve la ligne, on clique sur Supprimer
          cy.contains('tr', 'Cypress').find('button').contains('Supprimer').click()
          cy.on('window:confirm', () => true)
          
          cy.wait(1000) // On attend que la liste se rafraîchisse
          cleanAllCypressTeams() // On relance la fonction pour voir s'il en reste d'autres
        } else {
          cy.log('✨ Nettoyage terminé : La voie est libre !')
        }
      })
    }
    
    // Lancer le nettoyage
    cleanAllCypressTeams()

    // --- 2. CRÉATION ---
    cy.get('[data-cy=btn-create-team]').click()
    cy.get('[data-cy=input-company]').type(COMPANY_NAME)

    // Sélection des joueurs libres
    cy.contains('label', 'LibreA').scrollIntoView().should('be.visible').find('input[type="checkbox"]').check({force: true})
    cy.contains('label', 'LibreB').scrollIntoView().should('be.visible').find('input[type="checkbox"]').check({force: true})

    // Sauvegarder
    cy.get('[data-cy=btn-save-team]').click()

    // --- 3. VÉRIFICATION ---
    cy.wait('@createTeam').then((interception) => {
      if (interception.response.statusCode >= 400) {
        throw new Error(`🛑 LE BACKEND A REFUSÉ : ${JSON.stringify(interception.response.body)}`)
      }
    })

    cy.get('[data-cy=btn-save-team]').should('not.exist')
    cy.contains(COMPANY_NAME).should('be.visible')
    
    // --- 4. NETTOYAGE FINAL ---
    cy.contains('tr', COMPANY_NAME).find('button').contains('Supprimer').click()
    cy.on('window:confirm', () => true)
    cy.contains(COMPANY_NAME).should('not.exist')
  })
})