describe('Page Résultats & Classement', () => {
  
  context('En tant qu\'Administrateur', () => {
    beforeEach(() => {
      cy.visit('http://localhost:5173/login')
      cy.get('input[type="email"]').type('admin@padel.com')
      cy.get('input[type="password"]').type('Admin@2025!')
      cy.get('button[type="submit"]').click()
      cy.url().should('not.include', '/login')
    })

    it('Doit afficher le classement général', () => {
      // Intercepter la requête pour attendre le chargement
      cy.intercept('GET', '**/results/rankings').as('getRankings')

      cy.visit('http://localhost:5173/results')
      cy.wait('@getRankings')

      // Vérifier le titre
      cy.get('[data-cy=page-title]').should('contain', 'Résultats & Classement')

      // Vérifier que l'onglet Classement est actif
      cy.get('[data-cy=tab-ranking]').should('have.class', 'bg-blue-600')

      // Vérifier que le tableau est présent
      cy.get('[data-cy=ranking-table]').should('be.visible')

      // Vérifier qu'il y a des lignes dans le tableau (d'après le seed)
      cy.get('[data-cy=ranking-row]').should('have.length.at.least', 1)

      // Vérifier la présence de "Tech Corp" (qui a joué dans le seed)
      cy.contains('Tech Corp').should('be.visible')
    })

    it('Ne doit PAS voir l\'onglet "Mes Résultats" (réservé aux joueurs)', () => {
      cy.visit('http://localhost:5173/results')
      cy.get('[data-cy=tab-history]').should('not.exist')
    })
  })

  context('En tant que Joueur (Joueur1)', () => {
    // Joueur1 fait partie de "Tech Corp" qui a gagné un match dans seed_data.py
    beforeEach(() => {
      cy.visit('http://localhost:5173/login')
      cy.get('input[type="email"]').type('joueur1@test.com')
      cy.get('input[type="password"]').type('User@2025!')
      cy.get('button[type="submit"]').click()
      cy.url().should('not.include', '/login')
    })

    it('Doit voir ses statistiques personnelles et son historique', () => {
      // Interception des appels API
      cy.intercept('GET', '**/results/rankings').as('getRankings')
      cy.intercept('GET', '**/results/my-results').as('getMyResults')

      cy.visit('http://localhost:5173/results')
      
      // Cliquer sur l'onglet "Mes Résultats"
      cy.get('[data-cy=tab-history]').should('be.visible').click()
      
      // Attendre le chargement des données perso
      cy.wait('@getMyResults')

      // 1. Vérifier les cartes de stats
      // Joueur1 a gagné 1 match dans le seed -> Total: 1, Wins: 1
      cy.get('[data-cy=stat-total]').should('not.have.text', '0') 
      cy.get('[data-cy=stat-wins]').should('not.have.text', '0')

      // 2. Vérifier la liste d'historique
      cy.get('[data-cy=history-list]').should('exist')
      cy.get('[data-cy=history-item]').should('have.length.at.least', 1)

      // 3. Vérifier le détail du match
      // Il a joué contre "StartUp Z" (l'équipe adverse dans le seed)
      // Et le résultat doit être VICTOIRE
      cy.get('[data-cy=history-item]').first().within(() => {
        cy.contains('VICTOIRE').should('be.visible')
        cy.contains('vs').should('be.visible') 
      })
    })
  })
})