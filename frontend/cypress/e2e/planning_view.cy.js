describe('Gestion du Planning', () => {
  
  beforeEach(() => {
    cy.clearLocalStorage();
    // Interception globale des événements et des équipes
    cy.intercept('GET', `**/api/v1/events*`, { fixture: 'events.json' }).as('getEvents');
    cy.intercept('GET', `**/api/v1/teams*`, { fixture: 'teams.json' }).as('getTeams');
  });

  // Vue Utilisateur
  describe('Vue Utilisateur (Joueur)', () => {
    beforeEach(() => {
      cy.visit('http://localhost:5173/login');
      cy.get('input[type="email"]').type('pierre.dubois@datalab.com');
      cy.get('input[type="password"]').type('I!H9"5"l}4R)m<^h');
      cy.get('button[type="submit"]').click();

      // Attendre que la redirection soit faite
      cy.url().should('not.include', '/login');
      cy.visit('http://localhost:5173/planning');
      cy.wait('@getEvents');
    });

    it('Affiche le calendrier et navigue entre les mois', () => {
      cy.contains('h1', 'Planning').should('be.visible');
      
      // Vérifier la présence des jours de la semaine
      ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].forEach(day => {
        cy.contains(day).should('be.visible');
      });

      // Navigation : Mois précédent
      cy.get('button').contains('◀️').click();
      cy.wait('@getEvents');
      
      // Navigation : Mois suivant
      cy.get('button').contains('▶️').click();
      cy.wait('@getEvents');
    });

    it('Ouvre les détails d\'un jour contenant des événements', () => {
      // On attend que les badges indigo (événements) soient chargés
      cy.get('.bg-indigo-100', { timeout: 10000 }).first().click({ force: true });
      
      // La modale de détails (.fixed.inset-0)
      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        // Vérifie qu'une heure est affichée
        // Le format \d{2}:\d{2} cherche 2 chiffres, deux points, 2 chiffres
        cy.contains(/\d{2}:\d{2}/).should('be.visible');
        
        // Vérifie la présence du mot "Piste" (générique)
        cy.contains(/Piste \d+/).should('be.visible');
        
        // Vérifie qu'il y a un séparateur de match "vs"
        cy.contains(/vs/i).should('be.visible');

        // Fermeture
        cy.contains('button', 'Fermer').click();
      });

      cy.get('.fixed.inset-0').should('not.exist');
    });
  });

  // Vue Admin
  describe('Vue Administration', () => {
    beforeEach(() => {
      cy.visit('http://localhost:5173/login');
      cy.get('input[type="email"]').type('admin@padel.com');
      cy.get('input[type="password"]').type('Admin@2025!');
      cy.get('button[type="submit"]').click();

      cy.url().should('not.include', '/login');
      cy.visit('http://localhost:5173/planning');
      // L'admin charge les événements ET les équipes pour le formulaire
      cy.wait(['@getEvents', '@getTeams']);
    });

    it('Crée un nouvel événement avec succès', () => {
      cy.intercept('POST', `**/api/v1/events*`, { statusCode: 201 }).as('createEvent');

      cy.contains('button', 'Nouvel événement').click();

      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        // Calcul d'une date demain pour éviter le blocage du min="todayStr"
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateStr = tomorrow.toISOString().split('T')[0];

        cy.get('input[type="date"]').type(dateStr);
        cy.get('input[type="time"]').type('18:00');

        // Configurer le match (Sélecteurs basés sur l'ordre des selects dans ton template)
        cy.get('select').eq(0).select(2); // Piste 2
        cy.get('select').eq(1).select(1); // Équipe 1 (index 1 de la fixture teams)
        cy.get('select').eq(2).select(2); // Équipe 2 (index 2 de la fixture teams)

        cy.contains('button', 'Créer').click();
      });

      cy.wait('@createEvent');
      cy.get('.fixed.inset-0').should('not.exist');
    });


    it('Affiche une erreur si deux équipes identiques sont sélectionnées', () => {
      cy.contains('button', 'Nouvel événement').click();

      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        // On prend une date demain pour être sûr qu'elle soit valide (min="today")
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateStr = tomorrow.toISOString().split('T')[0];

        cy.get('input[type="date"]').type(dateStr);
        cy.get('input[type="time"]').type('14:00');

        // Sélectionner la même équipe (index 1) dans les deux menus
        // eq(1) = Equipe 1, eq(2) = Equipe 2
        cy.get('select').eq(1).select(1);
        cy.get('select').eq(2).select(1);
        
        // Cliquer sur Créer
        cy.contains('button', 'Créer').click();
        
        cy.contains('Une équipe ne peut pas jouer contre elle-même.').should('be.visible');
      });
    });
  });
});