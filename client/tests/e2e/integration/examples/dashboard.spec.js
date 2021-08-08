
describe('Dashboard', () => {
  it('redirects to login page', () => {
    cy.visit('/')
    cy.url().should('contain', '/login')
  })

  it('renders terms of service link', () => {
    cy.visit('/')
    cy.get('[href="/tos"]').should('contain', 'Terms of Service')
  })

  it('display signup link', () => {
    cy.visit('/')
    cy.get('[href="/signup"]').should('contain', "Don't have an account yet? Sign up now")
  })
})
