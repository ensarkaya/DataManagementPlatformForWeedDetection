import React, { ReactElement } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAppSelector } from "../../store/hooks";

interface ProtectedRouteProps {
  children?: ReactElement;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = useAppSelector((state) => state.auth.token); // Use RootState for correct typing
  const isAuthenticated = token !== null;

  if (!isAuthenticated) {
    // If the user is not authenticated, redirect them to the login page
    console.log("Not authenticated");
    return <Navigate to="/" replace />;
  }

  // If children is provided, render children, otherwise render Outlet
  return children || <Outlet />;
};

export default ProtectedRoute;
