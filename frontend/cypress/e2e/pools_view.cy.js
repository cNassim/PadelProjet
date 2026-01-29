describe('Gestion des Poules', () => {
  
  beforeEach(() => {
    cy.clearLocalStorage()
    
    // Interceptions globales
    cy.intercept('GET', '**/api/v1/pools*', { fixture: 'pools.json' }).as('getPools')
    cy.intercept('GET', '**/api/v1/teams*', { fixture: 'teams.json' }).as('getTeams')

    cy.visit('http://localhost:5173/login')
  })

  // Tests vue Utilisateur:
  describe('Vue Utilisateur (Joueur)', () => {
    beforeEach(() => {
      // Connexion
      cy.get('input[type="email"]').type('pierre.dubois@datalab.com')
      cy.get('input[type="password"]').type('I!H9"5"l}4R)m<^h')
      cy.get('button[type="submit"]').click()
      
      // Vérifier que le login a réussi
      cy.url().should('not.include', '/login')
      
      cy.visit('http://localhost:5173/pools')
      cy.wait('@getPools')
    })

    it('Affiche la liste des poules avec 6 équipes chacune', () => {
      cy.contains('h1', 'Poules').should('be.visible')
      
      // On vérifie la première carte de poule dans la grille
      cy.get('.grid > div').first().within(() => {
        cy.get('h2').should('be.visible') 
        // Vérifie la règle métier : 6 équipes affichées
        cy.get('ul li').should('have.length', 6)
        cy.contains('Équipes').should('be.visible')
      })
    })

    it('Ne doit pas afficher les options de gestion (que pour Admin)', () => {
      cy.contains('button', 'Nouvelle Poule').should('not.exist')
      cy.get('button[title="Supprimer la poule"]').should('not.exist')
      cy.contains('🗑️').should('not.exist')
    })
  })

 // Tests vue Admin:
  describe('Vue Administration', () => {
    beforeEach(() => {
      cy.visit('http://localhost:5173/login')
      cy.get('input[type="email"]').type('admin@padel.com')
      cy.get('input[type="password"]').type('Admin@2025!')
      cy.get('button[type="submit"]').click()
      
      cy.url().should('not.include', '/login')
      cy.visit('http://localhost:5173/pools')
      cy.wait(['@getPools', '@getTeams'])
    })

    it('Valide la création : bloqué si < 6 et limité à 6 équipes', () => {
      cy.contains('button', 'Nouvelle Poule').click()
      cy.get('h2').should('contain', 'Créer une nouvelle poule')
      
      cy.get('input[placeholder="Ex: Poule A"]').type('Poule Master')

      // Sélectionne 6 équipes (les 6 premières checkboxes)
      cy.get('input[type="checkbox"]').each(($el, index) => {
        if (index < 6) {
          cy.wrap($el).check()
        }
      })

      // Le compteur doit indiquer 6/6 et le bouton doit s'activer
      cy.contains('6 / 6 sélectionnées').should('be.visible')
      cy.get('button[type="submit"]').should('not.be.disabled')

      // La 7ème équipe doit être désactivée (disabled)
      cy.get('input[type="checkbox"]').eq(6).should('be.disabled')
    })

    it('Permet de modifier une poule existante (Nom et Équipes)', () => {
      cy.intercept('PUT', '**/api/v1/pools/*', { 
        statusCode: 200,
        body: { id: 1, name: "Poule Alpha", teams: [] } // Le schéma calculera teams_count
      }).as('updatePool')

      cy.get('button[title="Modifier la poule"]').first().click()
      cy.get('h2').should('contain', 'Modifier la poule')

      // Modifier le nom
      cy.get('input[placeholder="Ex: Poule A"]').clear().type('Poule Alpha')

      // on décoche une équipe et on en coche une autre
      cy.get('input[type="checkbox"]').first().uncheck()
      cy.contains('5 / 6 sélectionnées').should('be.visible')
      cy.get('button[type="submit"]').should('be.disabled') // Bloqué car != 6

      // On coche l'équipe 7 (AI Labs) qui est libre grâce au teams.json
      cy.get('input[type="checkbox"]').eq(6).check()
      
      // Valider l'envoi
      cy.contains('6 / 6 sélectionnées').should('be.visible')
      cy.get('button[type="submit"]').contains('Enregistrer les modifications').click()

      cy.wait('@updatePool')

      // Vérifie l'alerte de succès 
      cy.on('window:alert', (text) => {
        expect(text).to.contains('Poule modifiée')
      })
    })

    it('Affiche une erreur si des matchs sont déjà joués', () => {
      cy.intercept('PUT', '**/api/v1/pools/*', {
        statusCode: 400,
        body: { detail: "Impossible de modifier la poule : certains matchs ont déjà été joués." }
      }).as('updateError')

      cy.get('button[title="Modifier la poule"]').first().click()
      cy.get('button[type="submit"]').click()

      cy.wait('@updateError')
      // Vérifie que le message d'erreur rouge s'affiche
      cy.get('.bg-red-50').should('contain', 'Impossible de modifier la poule')
    })

    it('Affiche une erreur si une équipe est déjà assignée à une autre poule', () => {
      cy.intercept('POST', '**/api/v1/pools*', {
        statusCode: 400,
        body: { detail: "L'équipe 'AI Labs' est déjà assignée à une autre poule." }
      }).as('postError')

      cy.contains('button', 'Nouvelle Poule').click()
      
      // Utilisation du bon placeholder (celui de ton code : "Ex: Poule A")
      cy.get('input[placeholder="Ex: Poule A"]').first().type('Poule Conflit')
      
      // Cocher les 6 premières équipes
      cy.get('input[type="checkbox"]').each(($el, index) => {
        if (index < 6) {
          cy.wrap($el).check()
        }
      })
      
      cy.get('button[type="submit"]').click()
      
      cy.wait('@postError')
      
      // Vérification de l'affichage du message d'erreur rouge
      cy.get('.bg-red-50').should('contain', "L'équipe 'AI Labs' est déjà assignée")
    })
    // POULE EXISTANTE
    it('Peut supprimer une poule existante', () => {
      cy.intercept('DELETE', `**/api/v1/pools/*`, { statusCode: 204 }).as('deleteRequest')
      
      // On accepte la boîte de confirmation "Attention : Supprimer une poule..."
      cy.on('window:confirm', () => true)

      cy.get('button[title="Supprimer la poule"]').first().click()
      
      cy.wait('@deleteRequest')
    })

    // NOM DE POULE DEJA EXISTANT
    it('Affiche une erreur si le nom de la poule est déjà pris', () => {
        cy.intercept('POST', '**/api/v1/pools*', {
            statusCode: 422,
            body: { detail: "Cette poule existe déjà" }
        }).as('postError')

        cy.contains('button', 'Nouvelle Poule').click()
        cy.get('input[placeholder="Ex: Poule A"]').type('Doublon')
        
        // On coche les 6 premières checkboxes
        cy.get('input[type="checkbox"]').each(($el, index) => {
            if (index < 6) {
            cy.wrap($el).check()
            }
        })
        
        cy.get('button[type="submit"]').click()
        cy.wait('@postError')
        
        cy.get('.bg-red-50').should('contain', 'Cette poule existe déjà')
        })
  })
})