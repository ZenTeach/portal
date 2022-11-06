describe('Login', () => {
  before(() => {
    cy.automock("login");
  });

  after(() => {
    cy.automockEnd();
  });

  it('logs in a user successfully', () => {
    cy.visit('/login')
    cy.get('#user-email').text(Cypress.env())
    cy.get('#user-password').text(Cypress.env())
    cy.get('button').click()

    cy.url().should('contain', '/')
  })
})
