import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import Admin from './pages/Admin';
import PostForm from './pages/PostForm';

const { Header, Content, Footer } = Layout;

function App() {
  return (
    <Router>
      <Layout className="layout" style={{ minHeight: '100vh' }}>
        <Header>
          <Navigation />
        </Header>
        <Content style={{ padding: '50px', backgroundColor: '#fff' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/create-post" element={<PostForm />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          公益账号分享平台 ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Router>
  );
}

export default App;
