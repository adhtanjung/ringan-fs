export default defineNuxtRouteMiddleware((to, from) => {
	// TEMPORARILY DISABLED: Admin authentication bypass for development
	// TODO: Re-enable authentication when admin login is restored

	/* ORIGINAL AUTHENTICATION CODE - PRESERVED FOR RESTORATION:
  // Check if user is authenticated and has admin role
  const authToken = useCookie('auth-token')
  const userRole = useCookie('user-role')

  if (!authToken.value) {
    // Redirect to login if not authenticated
    return navigateTo('/auth/login')
  }

  if (userRole.value !== 'admin') {
    // Redirect to home if not admin
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied. Admin privileges required.'
    })
  }
  */

	// Currently allowing all access to admin routes
	// Remove this comment and uncomment the above code to restore authentication
	return;
});
