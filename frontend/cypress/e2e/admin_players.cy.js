describe('Gestion des Joueurs - Admin', () => {
    beforeEach(() => {
        cy.clearLocalStorage()
        // Connexion en tant qu'admin
        cy.visit('/login')
        cy.get('input[type="email"]').type('admin@padel.com')
        cy.get('input[type="password"]').type('Admin@2025!')
        cy.get('button[type="submit"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + '/')

        // Aller sur la page Admin
        cy.contains('Administration').click()
        cy.url().should('include', '/admin')
    })

    it('Ajouter, modifier puis supprimer un joueur', () => {
        const randomSuffix = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5)
        const playerName = 'TestPlayer' + randomSuffix
        const playerLicense = 'L' + Math.floor(100000 + Math.random() * 900000)

        // 1. Ajouter un joueur
        cy.contains('Joueurs').click()
        cy.contains('+ Nouveau joueur').click()

        cy.get('input[required]').eq(0).type('Cypress') // Prénom
        cy.get('input[required]').eq(1).type(playerName) // Nom
        cy.contains('label', 'Entreprise').next('input').type('TestCorp')
        cy.contains('label', 'Numéro de licence').next('input').type(playerLicense)
        cy.get('input[type="date"]').type('1990-01-01')

        cy.get('button[type="submit"]').click()

        // Vérifier l'ajout
        cy.contains(playerName).should('be.visible')
        cy.contains('TestCorp').should('be.visible')

        // 2. Modifier le joueur
        cy.contains('tr', playerName).find('button').contains('✏️').click()
        cy.contains('label', 'Entreprise').next('input').clear().type('UpdatedCorp')
        cy.get('button[type="submit"]').click()

        cy.contains(playerName).should('be.visible')
        cy.contains('UpdatedCorp').should('be.visible')

        // 3. Supprimer le joueur
        cy.contains('tr', playerName).find('button').contains('❌').click()
        // Confirmer l'alert (Cypress le fait automatiquement par défaut si alert/confirm)
        cy.on('window:confirm', () => true)

        // Vérifier la suppression
        cy.contains(playerName).should('not.exist')
    })

    it('Rechercher un joueur', () => {
        cy.contains('Joueurs').click()
        // Attendre que le chargement soit fini (évite de matcher '10 joueurs' avec '0 joueurs')
        cy.get('.text-gray-500.font-medium').should('not.have.text', 'Total: 0 joueurs')

        cy.get('input[placeholder="Rechercher..."]').type('Marie')
        cy.get('tbody tr').should('have.length.at.least', 1).each(($tr) => {
            cy.wrap($tr).should('contain', 'Marie')
        })
    })
})
