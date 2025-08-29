export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    
    // Validate required fields
    const { email, password } = body
    
    if (!email || !password) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Email dan password harus diisi'
      })
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Format email tidak valid'
      })
    }

    // Here you would typically:
    // 1. Find user by email in database
    // 2. Compare hashed password
    // 3. Generate JWT token
    // 4. Return user data and token

    // Mock user data for demo
    const mockUsers = [
      {
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123' // In real app, this would be hashed
      },
      {
        id: 2,
        name: 'Jane Smith',
        email: 'jane@example.com',
        password: 'mypassword'
      }
    ]

    // Find user by email
    const user = mockUsers.find(u => u.email.toLowerCase() === email.toLowerCase())
    
    if (!user) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Email atau password salah'
      })
    }

    // Check password (in real app, compare with hashed password)
    if (user.password !== password) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Email atau password salah'
      })
    }

    // Log successful login
    console.log('User logged in:', {
      id: user.id,
      name: user.name,
      email: user.email
    })

    // Return success response (without password)
    return {
      success: true,
      message: 'Login successful',
      user: {
        id: user.id,
        name: user.name,
        email: user.email
      },
      // In real app, you would return a JWT token
      token: `mock_jwt_token_${user.id}_${Date.now()}`
    }

  } catch (error: any) {
    // Handle known errors
    if (error.statusCode) {
      throw error
    }

    // Handle unexpected errors
    console.error('Login error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error'
    })
  }
}) 