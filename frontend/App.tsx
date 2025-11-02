import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider, MD3DarkTheme } from 'react-native-paper';
import Toast from 'react-native-toast-message';

import AppNavigator from './src/navigation/AppNavigator';
import { AuthProvider } from './src/context/AuthContext';

const theme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#4ade80',
    background: '#050912',
    surface: '#101727',
    onSurface: '#f8fafc',
  },
};

const App = () => {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <AuthProvider>
          <AppNavigator />
          <Toast position="top" topOffset={50} />
        </AuthProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
};

export default App;

