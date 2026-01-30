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

    it('Comportement compte neuf : n\'affiche rien par défaut et affiche tout si on coche', () => {
      // Interceptions
      cy.intercept('GET', '**/api/v1/events?*show_all=false*', { body: { events: [] } }).as('getMyEventsEmpty');
      cy.intercept('GET', '**/api/v1/events?*show_all=true*', { fixture: 'events.json' }).as('getAllEvents');

      cy.visit('http://localhost:5173/planning');
      cy.wait('@getMyEventsEmpty');

      // 1. Vérifier que le calendrier est vide visuellement
      cy.get('.bg-indigo-100').should('not.exist');

      // 2. Ouvrir la modale en cliquant sur un jour (ex: le 15)
      cy.contains('span', '15').click({ force: true });

      // 3. Vérifier le message d'absence d'événement DANS la modale
      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        cy.contains('Aucun événement prévu ce jour.').should('be.visible');
        // Fermer la modale pour la suite du test
        cy.get('button').contains(/Fermer|✖️/).click();
      });

      // 4. Cocher la case pour tout voir
      cy.get('input[type="checkbox"]').check();
      cy.wait('@getAllEvents');

      // 5. Vérifier que les badges sont maintenant là
      cy.get('.bg-indigo-100').should('have.length.at.least', 1);
    });

    it('Affiche tous les événements après avoir coché "Voir tous les événements"', () => {
      // Stub de l'API
      cy.intercept('GET', '/api/events*', { fixture: 'events.json' }).as('getEvents');

      cy.visit('/planning');

      // Attendre que le loader disparaisse
      cy.get('.inline-block.animate-spin', { timeout: 10000 }).should('not.exist');

      // Cocher la checkbox pour voir tous les événements
      cy.get('input[type="checkbox"]').check({ force: true });

      // Attendre que les badges indigo apparaissent
      cy.get('.bg-indigo-100', { timeout: 10000 }).should('have.length.greaterThan', 0);

      // Cliquer sur le premier événement
      cy.get('.bg-indigo-100').first().click({ force: true });

      // Vérifier la modale
      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        cy.contains(/\d{2}:\d{2}/).should('be.visible'); // Heure
        cy.contains(/Piste \d+/).should('be.visible');    // Numéro de piste
        cy.contains(/vs/i).should('be.visible');         // "vs"

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

    it('Vérifie les règles de suppression selon le statut du match', () => {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const datePresente = `${year}-${month}-15`; // Milieu du mois actuel

      cy.intercept('GET', '**/api/v1/events*', {
        body: {
          events: [
            {
              id: 99,
              event_date: datePresente,
              event_time: "10:00:00",
              matches: [{ id: 500, status: "TERMINE", team1: {company: "A"}, team2: {company: "B"} }]
            }
          ]
        }
      }).as('getPastEvents');

      cy.visit('http://localhost:5173/planning');
      cy.wait('@getPastEvents');

      //affichage du badge
      cy.get('.bg-indigo-100', { timeout: 10000 }).first().click({ force: true });

      // verification du regle métier
      cy.get('.fixed.inset-0').within(() => {
        // Si le match est TERMINE, le bouton supprimer ne doit pas être là
        cy.contains('Terminé').should('be.visible');
        cy.contains('button', '🗑️ Supprimer').should('not.exist');
      });
    });

    //Test Doublon de Piste
    it('Affiche une erreur si la même piste est utilisée deux fois dans le même événement', () => {
      cy.contains('button', 'Nouvel événement').click();

      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        // Remplissage des prérequis
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateStr = tomorrow.toISOString().split('T')[0];

        cy.get('input[type="date"]').type(dateStr);
        cy.get('input[type="time"]').type('18:00');

        // Ajout d'un deuxième match
        cy.contains('button', '+ Ajouter un match').click();

        // Configuration des matchs sur la même piste (Piste 1)
        // Match 1 : Piste 1, Equipe 1, Equipe 2
        cy.get('select').eq(0).select('1'); 
        cy.get('select').eq(1).select(1); 
        cy.get('select').eq(2).select(2); 

        // Match 2 : Piste 1 (doublon), Equipe 3, Equipe 4
        cy.get('select').eq(3).select('1'); 
        cy.get('select').eq(4).select(3); 
        cy.get('select').eq(5).select(4); 

        // Tentative de création
        cy.contains('button', 'Créer').click();

        // Vérification de l'erreur métier
        cy.contains('Erreur : Vous avez sélectionné la même piste pour plusieurs matchs.')
          .should('be.visible');
      });
    });

    //test de doublon de match
    it('Affiche une erreur si une équipe est inscrite sur deux matchs différents le même jour', () => {
      cy.contains('button', 'Nouvel événement').click();

      cy.get('.fixed.inset-0').should('be.visible').within(() => {
        // Prérequis (Date/Heure)
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateStr = tomorrow.toISOString().split('T')[0];
        cy.get('input[type="date"]').type(dateStr);
        cy.get('input[type="time"]').type('18:00');

        cy.contains('button', '+ Ajouter un match').click();

        // Configuration Match 1 (Piste 1 par défaut)
        cy.get('select').eq(1).select(1); // Team 1
        cy.get('select').eq(2).select(2); // Team 2
        
        // Config du 2e Match
        //On change la piste pour eq(3) pour éviter le conflit de piste
        cy.get('select').eq(3).select('2'); 
        
        // On sélectionne l'équipe doublon
        cy.get('select').eq(4).select(1); // Team 1 (Déjà dans match 1)
        cy.get('select').eq(5).select(3); // Team 2

        cy.contains('button', 'Créer').click();

        // Vérification de l'erreur métier
        cy.contains('Erreur : Une équipe ne peut pas jouer deux matchs lors du même événement.')
          .should('be.visible');
      });
    });

    it('Affiche une erreur si on choisit la meme équipe pour jouer contre elle-même', () => {
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