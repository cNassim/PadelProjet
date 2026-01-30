describe('Système Padel - Tests Complets', () => {
  
  beforeEach(() => {
    cy.clearLocalStorage()
    // Interceptions globales utilisées dans les différents tests
    cy.intercept('GET', '**/api/v1/pools*', { fixture: 'pools.json' }).as('getPools')
    cy.intercept('GET', '**/api/v1/teams*', { fixture: 'teams.json' }).as('getTeams')
    cy.intercept('GET', '**/profile/me', { fixture: 'profile.json' }).as('getProfile')

    cy.visit('http://localhost:5173/login')
  })
  
  describe('Vue Utilisateur (Profil)', () => {
    beforeEach(() => {
      // Connexion en tant que joueur
      cy.get('input[type="email"]').type('pierre.dubois@datalab.com')
      cy.get('input[type="password"]').type('I!H9"5"l}4R)m<^h')
      cy.get('button[type="submit"]').click()

      // Vérifier que le login a réussi
      cy.url().should('not.include', '/login')
      
      cy.visit('http://localhost:5173/profile')
      cy.wait('@getProfile')
    })

    it('affiche correctement les informations du joueur issues de la fixture', () => {
      cy.get('h1').should('contain', 'Mon Profil')
      cy.get('input[type="email"]').should('have.value', 'test@techcorp.com')
      cy.contains('label', 'Prénom').next('input').should('have.value', 'Jean')
      cy.contains('label', 'Nom').next('input').should('have.value', 'Dupont')
    })

    it('permet de changer d\'onglet entre Informations et Mot de passe', () => {
      cy.contains('button', 'Mot de passe').click()
      cy.get('h2').should('contain', 'Changer mon mot de passe')
      cy.contains('button', 'Informations').click()
      cy.get('h2').should('contain', 'Mes informations')
    })

    it('met à jour les informations avec succès', () => {
      cy.intercept('PUT', '**/profile/me', {
        statusCode: 200,
        body: {
          message: "Profil mis à jour avec succès",
          profile: {
            user: { id: 1, email: "update@techcorp.com", role: "JOUEUR" },
            player: { id: 1, first_name: "Jean", last_name: "Dupont", company: "TechCorp", birth_date: "1995-06-15", photo_url: null }
          }
        }
      }).as('updateProfile')

      cy.get('input[type="email"]').clear().type('update@techcorp.com')
      cy.get('button[type="submit"]').contains('Enregistrer').click()
      cy.wait('@updateProfile')
      cy.get('.bg-green-50').should('contain', '✅ Profil mis à jour avec succès')
    })

    it('affiche une erreur si le changement de mot de passe échoue', () => {
      cy.intercept('POST', '**/profile/me/password', {
        statusCode: 400,
        body: { detail: "Le mot de passe actuel est incorrect" }
      }).as('passwordError')

      cy.contains('button', 'Mot de passe').click()
      cy.get('input[type="password"]').first().type('mauvais_pass')
      cy.get('input[type="password"]').eq(1).type('NouveauPass123!')
      cy.get('input[type="password"]').eq(2).type('NouveauPass123!')
      cy.get('button[type="submit"]').click()

      cy.wait('@passwordError')
      cy.get('.bg-red-50').should('contain', 'Le mot de passe actuel est incorrect')
    })

    it('gère l\'upload de photo de profil (Base64)', () => {
      cy.intercept('POST', '**/profile/me/photo', {
        statusCode: 200,
        body: { message: "Photo mise à jour", photo_url: "data:image/png;base64,mockdata" }
      }).as('uploadPhoto')

      cy.get('input[type="file"]').selectFile({
        contents: Cypress.Buffer.from('SGVsbG8gV29ybGQ='),
        fileName: 'avatar.png',
        mimeType: 'image/png',
      }, { force: true })

      cy.wait('@uploadPhoto')
      cy.get('.bg-green-50').should('contain', '✅ Photo mise à jour !')
    })
  })
})