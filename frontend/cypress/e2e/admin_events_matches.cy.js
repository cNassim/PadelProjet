describe('Gestion des Événements et Matchs - Admin', () => {
    beforeEach(() => {
        cy.clearLocalStorage()
        // Connexion en tant qu'admin
        cy.visit('/login')
        cy.get('input[type="email"]').type('admin@padel.com')
        cy.get('input[type="password"]').type('Admin@2025!')
        cy.get('button[type="submit"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + '/')
    })

    it('Créer, voir puis supprimer un événement', () => {
        cy.contains('Planning').click()
        
        const today = new Date()
        if (today.getDate() > 28) {
            cy.get('button').contains('▶️').click()
            cy.wait(500) 
        }

        cy.contains('Nouvel événement').click()

        const targetDate = new Date()
        if (today.getDate() > 28) targetDate.setMonth(targetDate.getMonth() + 1)
        const dateStr = `${targetDate.getFullYear()}-${String(targetDate.getMonth() + 1).padStart(2, '0')}-28`

        cy.get('.fixed.inset-0').within(() => {
            cy.get('input[type="date"]').type(dateStr)
            cy.get('input[type="time"]').type('19:00')
            cy.get('select').eq(1).select(1) 
            cy.get('select').eq(2).select(2)
            cy.contains('button', 'Créer').click()
        })

        cy.contains('.relative', '28').click()
        cy.contains('19:00').should('be.visible')
        
        cy.on('window:confirm', () => true)
        cy.contains('🗑️ Supprimer').click()

        // Vérifier la disparition
        cy.contains('19:00').should('not.exist')
    })

    it('Mettre à jour le score d\'un match', () => {
        cy.contains('Matchs').click()
        cy.url().should('include', '/matches')

        // Attendre que le chargement soit fini
        cy.get('.animate-spin').should('not.exist')

        // S'assurer qu'il y a des matchs
        cy.get('.space-y-4 > .bg-white').should('have.length.gt', 0)

        // Trouver le premier match "À venir"
        cy.get('.space-y-4').contains('.bg-white', 'À venir').first().as('matchCard')

        cy.get('@matchCard').contains('✏️ Éditer').click()

        // Interagir avec la modal
        cy.get('.fixed.inset-0').should('be.visible').within(() => {
            // Changer le statut en Terminé
            cy.get('select').first().select('TERMINE')

            // Saisir les scores
            cy.get('input[placeholder*="6-4"]').eq(0).clear().type('6-0, 6-0')
            cy.get('input[placeholder*="4-6"]').eq(0).clear().type('0-6, 0-6')

            cy.contains('button', 'Enregistrer').click()
        })

        // Attendre la fermeture de la modal
        cy.get('.fixed.inset-0').should('not.exist')

        // Vérifier la mise à jour
        cy.contains('6-0, 6-0').should('be.visible')
        cy.contains('Terminé').should('be.visible')
    })
})