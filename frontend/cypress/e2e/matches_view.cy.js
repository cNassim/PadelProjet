describe('Gestion des Matchs', () => {
  
  beforeEach(() => {

    cy.clearLocalStorage()

    // correction de l'url vu le conflit avec le cy.visit
    cy.intercept('GET', '**/api/v1/matches*', { fixture: 'matches.json' }).as('getMatches')
  })

  // View du coté de l'utilisateur
  describe('Vue Utilisateur (Joueur)', () => {

    beforeEach(() => {
      //navigation vers la page login
      cy.visit('http://localhost:5173/login')

      // Connection avec les credentiels Utilisateur
      cy.get('input[type="email"]').type('pierre.dubois@datalab.com')
      cy.get('input[type="password"]').type('I!H9"5"l}4R)m<^h')
      cy.get('button[type="submit"]').click()

      //test de la connection réussie
      cy.url().should('not.include', '/login')
      
      // Navigation et attente explicite
      cy.visit('http://localhost:5173/matches')
      cy.wait('@getMatches') 
    })

    // Tests affichage des infos
    it('Affiche les informations des matchs (équipes, scores, date)', () => {
      cy.contains('h1', 'Matchs').should('be.visible')
      cy.contains('Terminé').should('be.visible')
      cy.contains('6-4, 6-2').should('be.visible')
      cy.contains('À venir').should('be.visible')
    })

    //Tests de filtre 
    it('Permet de filtrer par "Mes matchs"', () => {
      cy.intercept('GET', '**/api/v1/matches?*my_matches=*').as('filterMatches')
      
      // On force le déclenchement du filtre
      cy.get('input[type="checkbox"]').first().uncheck()
      cy.wait('@filterMatches')
      cy.get('input[type="checkbox"]').first().check()
      cy.wait('@filterMatches').its('request.url').should('include', 'my_matches=true')
    })
  })

  // View coté admiin
  describe('Vue Administration', () => {
    beforeEach(() => {
      cy.visit('http://localhost:5173/login')

      // connection avec credentiels admin
      cy.get('input[type="email"]').type('admin@padel.com')
      cy.get('input[type="password"]').type('Admin@2025!')
      cy.get('button[type="submit"]').click()
      
      //test de navigation
      cy.url().should('not.include', '/login')
      
      cy.intercept('GET', '**/api/v1/matches*', { fixture: 'matches.json' }).as('getMatchesAdmin')
      cy.visit('http://localhost:5173/matches')

      // attente du chargement des données tests
      cy.wait('@getMatchesAdmin')
    })

    // édition du score d'un match
    it('Ouvre la modale et édite le score d’un match', () => {
        // changement de PATCH par PUT vu le service
      cy.intercept('PUT', '**/api/v1/matches/*', { statusCode: 200 }).as('updateMatch')
      
      // On cible le premier match "À venir" pour avoir le bouton Éditer
      cy.get('.space-y-4').contains('.bg-white', 'À venir').first().within(() => {
        cy.contains('button', '✏️ Éditer').click()
      })
      
      // Dans la modale (fixed inset-0)
      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        // eq(0) car c'est le premier select DANS la modale
        cy.get('select').first().select('TERMINE') 
        
        // Remplissage des scores
        cy.get('input[placeholder*="6-4"]').clear().type('6-0, 6-0')
        cy.get('input[placeholder*="4-6"]').clear().type('0-6, 0-6')
        
        cy.contains('button', 'Enregistrer').click()
      })
      
      cy.wait('@updateMatch')
      cy.get('.fixed.inset-0').should('not.exist')
    })

    // Test de la règle métier : Suppression uniquement si A_VENIR
    it('Ne doit pas afficher le bouton de suppression pour un match Terminé', () => {

      //verif s'il y a un match terminé avant le test
      cy.get('.space-y-4').contains('.bg-white', 'Terminé').first().within(() => {
        cy.contains('button', '🗑️ Suppr.').should('not.exist');
      });
    });

    // Test des filtres
    it('Permet à l\'admin de filtrer les matchs par chaque statut', () => {
      const statuses = [
        { value: 'TERMINE', label: 'Terminé' },
        { value: 'A_VENIR', label: 'À venir' },
        { value: 'ANNULE', label: 'Annulé' }
      ];

      statuses.forEach(({ value, label }) => {
        // Interception de l'appel API avec le paramètre de statut
        cy.intercept('GET', `**/api/v1/matches?*status=${value}*`).as(`filter${value}`);
        
        // Sélection du statut dans le menu
        cy.get('select').first().select(value);
        
        // Attente du retour API
        cy.wait(`@filter${value}`);

        // On vérifie l'affichage de manière globale dans la page
        cy.get('body').then(($body) => {
          if ($body.find('.space-y-4').length > 0) {
            // Si des matchs existent, on vérifie que le label est présent
            cy.contains(label).should('be.visible');
          } else {
            // Sinon, on vérifie que le message "Aucun match" est affiché
            cy.contains('Aucun match trouvé pour ces critères.').should('be.visible');
            cy.contains('📭').should('be.visible');
          }
        });
      });
    });


    //tets de suppression d'un match
    it('Supprime un match après confirmation', () => {
      cy.intercept('DELETE', '**/api/v1/matches/*', { statusCode: 204 }).as('deleteRequest')
      cy.on('window:confirm', () => true)

      cy.contains('button', '🗑️ Suppr.').first().click()
      cy.wait('@deleteRequest')
    })
  })
})