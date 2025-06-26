export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return {
          status,
          message: data.message || 'Invalid request',
          details: data.errors
        };
      case 401:
        return {
          status,
          message: 'Session expired - please login again',
          redirect: '/login?session=expired'
        };
      case 403:
        return {
          status,
          message: 'You are not authorized to access this resource'
        };
      case 422:
        return {
          status,
          message: data.message || 'Validation failed',
          details: data.errors
        };
      case 500:
        return {
          status,
          message: 'Server error - please try again later'
        };
      default:
        return {
          status,
          message: `Request failed with status ${status}`,
          details: data
        };
    }
  } else if (error.request) {
    // No response received
    return {
      status: 0,
      message: 'Network error - please check your connection'
    };
  } else {
    // Setup error
    return {
      status: -1,
      message: 'Application error - please refresh the page'
    };
  }
};