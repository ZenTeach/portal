export default {
  loginUser: jest.fn(payload =>
    Promise.resolve({
      data: {}
    })
  ),
  logoutUser: jest.fn(payload =>
    Promise.resolve({
      data: {}
    })
  ),
  registerUser: jest.fn(payload =>
    Promise.resolve({
      data: {}
    })
  ),
  getCurrentUser: jest.fn(payload =>
    Promise.resolve({
      data: {}
    })
  )
}
