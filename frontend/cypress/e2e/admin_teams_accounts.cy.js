describe('Administration Complète - Équipes et Comptes', () => {
    beforeEach(() => {
        cy.clearLocalStorage()
        cy.visit('/login')
        cy.get('input[type="email"]').type('admin@padel.com')
        cy.get('input[type="password"]').type('Admin@2025!')
        cy.get('button[type="submit"]').click()
        cy.url().should('eq', Cypress.config().baseUrl + '/')
    })

    const generateName = (prefix) => prefix + Math.random().toString(36).replace(/[^a-z]+/g, '').substring(0, 6)

    const createPlayer = (name) => {
        cy.contains('Administration').click()
        cy.contains('+ Nouveau joueur').click()
        cy.get('input[required]').eq(0).type('Test')
        cy.get('input[required]').eq(1).type(name)
        cy.contains('label', 'Entreprise').next('input').type('CypressCorp')
        cy.contains('label', 'Numéro de licence').next('input').type('L' + Math.floor(Math.random() * 1000000))
        cy.get('input[type="date"]').type('1990-01-01')
        cy.get('button[type="submit"]').click()
        cy.contains(name, { timeout: 10000 }).should('be.visible')
    }

    it('Gestion Équipes, Comptes et Permissions', () => {
        // --- 1. Gestion des Équipes ---
        const p1 = generateName('Alpha')
        const p2 = generateName('Beta')
        createPlayer(p1)
        createPlayer(p2)

        cy.contains('Équipes').click()
        cy.contains('Créer une équipe').click()
        cy.get('input[placeholder="Nom de l\'entreprise"]').type('Team ' + p1)
        cy.contains('label', p1).find('input').check()
        cy.contains('label', p2).find('input').check()
        cy.contains('button', 'Enregistrer').click()
        cy.contains('Team ' + p1).should('be.visible')

        // --- 2. Gestion des Comptes ---
        const pName = generateName('User')
        createPlayer(pName)

        // On repasse par l'accueil pour forcer un rechargement propre
        cy.visit('/')
        cy.contains('Administration').click()
        cy.contains('Comptes').click()
        cy.contains('Créer un compte').click()

        // Attendre que le joueur apparaisse (on peut avoir besoin de plusieurs reloads si le cache Vue est têtu)
        // Mais cy.visit('/') + click devrait suffire car AdminPage onMounted appelle loadPlayersWithoutAccount
        cy.get('select#playerId').should('contain', pName)
        cy.get('select#playerId option').contains(pName).then($opt => {
            cy.get('select#playerId').select(String($opt.val()))
        })
        cy.contains('button', 'Créer le compte').click()
        cy.contains('Compte créé avec succès', { timeout: 10000 }).should('be.visible')

        // --- 3. Permissions ---
        cy.get('.select-all').first().then($el => {
            const tempPass = $el.text().trim()
            cy.contains('Email :').next().then($emailEl => {
                const actualEmail = $emailEl.text().trim()

                cy.contains('Déconnexion').click()
                cy.wait(1000)

                cy.visit('/login')
                cy.get('input[type="email"]').type(actualEmail)
                cy.get('input[type="password"]').type(tempPass)
                cy.get('button[type="submit"]').click()

                cy.url().should('eq', Cypress.config().baseUrl + '/')
                cy.contains('Administration').should('not.exist')

                cy.visit('/admin', { failOnStatusCode: false })
                cy.url().should('eq', Cypress.config().baseUrl + '/')
            })
        })
    })
})
