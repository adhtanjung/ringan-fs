export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    
    // Validate required fields
    const { name, email, password, marketing_source, marketing_source_custom } = body
    
    if (!name || !email || !password || !marketing_source) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Missing required fields'
      })
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invalid email format'
      })
    }

    // Validate password length
    if (password.length < 6) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Password must be at least 6 characters'
      })
    }

    // Validate name length
    if (name.trim().length < 3) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Name must be at least 3 characters'
      })
    }

    // Here you would typically:
    // 1. Check if email already exists in database
    // 2. Hash the password
    // 3. Save user to database
    // 4. Send welcome email
    // 5. Return user data (without password)

    // Simulate checking if email exists
    const existingEmails = ['test@example.com', 'admin@ringan.com'] // Mock existing emails
    if (existingEmails.includes(email.toLowerCase())) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Email sudah digunakan'
      })
    }

    // Simulate saving to database
    const newUser = {
      id: Date.now(),
      name: name.trim(),
      email: email.toLowerCase(),
      marketing_source,
      marketing_source_custom: marketing_source === 'other' ? marketing_source_custom : null,
      created_at: new Date().toISOString(),
      // password would be hashed in real implementation
    }

    // Log the registration for demo purposes
    console.log('New user registered:', {
      name: newUser.name,
      email: newUser.email,
      marketing_source: newUser.marketing_source,
      marketing_source_custom: newUser.marketing_source_custom
    })

    // Return success response (without password)
    return {
      success: true,
      message: 'Registration successful',
      user: {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email
      }
    }

  } catch (error: any) {
    // Handle known errors
    if (error.statusCode) {
      throw error
    }

    // Handle unexpected errors
    console.error('Registration error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error'
    })
  }
}) 