import registerAutoMockCommands from 'cypressautomocker/include-in-tests';
registerAutoMockCommands();


beforeEach(function() {
  cy.on('window:before:load', win => {
    win.fetch = null;
  });
});
