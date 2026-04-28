import { useState, useEffect, useRef } from 'react';
import { Package, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Edges } from '@react-three/drei';
import './App.css';

// --- Visualizador 3D ---
function BoxWireframe({ args }) {
  return (
    <mesh>
      <boxGeometry args={args} />
      <meshBasicMaterial color="#22c55e" transparent opacity={0.1} />
      <Edges color="#16a34a" />
    </mesh>
  );
}

function ItemMesh({ position, args, color }) {
  return (
    <mesh position={position}>
      <boxGeometry args={args} />
      <meshStandardMaterial color={color} transparent opacity={0.9} />
      <Edges color="black" />
    </mesh>
  );
}

function Visualizer3D({ boxDimensions, items }) {
  return (
    <Canvas camera={{ position: [20, 20, 20], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 10]} intensity={1} />
      
      {/* Caja exterior */}
      <BoxWireframe args={boxDimensions} />

      {/* Ítems internos */}
      {items.map((item, index) => (
        <ItemMesh 
          key={index} 
          position={item.position} 
          args={item.dimensions} 
          color={item.color || '#3b82f6'} 
        />
      ))}
      
      <OrbitControls enablePan={false} maxPolarAngle={Math.PI / 2} />
    </Canvas>
  );
}

// --- Componente Global de Escáner ---
function GlobalScannerInput({ onScan }) {
  const inputRef = useRef(null);
  const [value, setValue] = useState('');

  // Mantener el foco siempre en este input oculto
  useEffect(() => {
    const focusInput = () => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    };
    
    focusInput();
    window.addEventListener('click', focusInput);
    window.addEventListener('blur', focusInput);
    
    return () => {
      window.removeEventListener('click', focusInput);
      window.removeEventListener('blur', focusInput);
    };
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (value.trim()) {
        onScan(value.trim());
        setValue('');
      }
    }
  };

  return (
    <input
      ref={inputRef}
      type="text"
      className="global-scanner"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onKeyDown={handleKeyDown}
      autoFocus
      autoComplete="off"
    />
  );
}

// --- App Principal ---
function App() {
  const [status, setStatus] = useState('IDLE'); // IDLE, LOADING, SUCCESS, ERROR
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Simular la llamada al backend real
  const fetchOrderPacking = (orderId) => {
    setStatus('LOADING');
    console.log(`Buscando pedido: ${orderId}`);
    
    // Simulación de respuesta basada en los casos de prueba (Caso 2: Textil)
    setTimeout(() => {
      if (orderId.includes('ERR')) {
        setStatus('ERROR');
        setError({ message: 'Pedido no encontrado o dimensiones inválidas.' });
      } else {
        setStatus('SUCCESS');
        setResult({
          orderId: orderId,
          boxModel: 'CAJA MODELO B',
          boxDetails: '40x30x20 cm',
          boxDimensions: [40, 20, 30], // Ancho, Alto, Profundo
          items: [
            { id: 'pantalon', dimensions: [38, 5, 28], position: [0, -7.5, 0], color: '#3b82f6' },
            { id: 'camisetas', dimensions: [20, 10, 20], position: [-9, 0, 0], color: '#f59e0b' },
            { id: 'cinturon', dimensions: [15, 5, 10], position: [10, -2.5, 5], color: '#ef4444' }
          ]
        });
      }
    }, 800); // 800ms latencia simulada
  };

  const resetState = () => {
    setStatus('IDLE');
    setResult(null);
    setError(null);
  };

  return (
    <div className="app-container">
      {/* Input Global - "Zero Clics" */}
      {status !== 'LOADING' && (
        <GlobalScannerInput onScan={fetchOrderPacking} />
      )}

      {/* Header */}
      <header className="header">
        <div className="logo">
          <Package size={32} color="#22c55e" />
          REDIMENSION Pick & Pack
        </div>
        <div className="operator-status">
          <span>Operario: <strong>Juan P.</strong></span>
          <span>Turno: <strong>Mañana</strong></span>
        </div>
      </header>

      {/* Contenido Principal */}
      <main className="main-content">
        
        {status === 'IDLE' && (
          <div className="idle-container">
            <Package className="idle-icon" />
            <h1 className="idle-title">ESCANEA EL CÓDIGO DE BARRAS</h1>
            <p className="idle-subtitle">(El sistema está listo y esperando input)</p>
            <div className="scanner-status">[ Scanner Activo ]</div>
          </div>
        )}

        {status === 'LOADING' && (
          <div className="idle-container">
            <h1 className="idle-title" style={{ color: '#f59e0b' }}>PROCESANDO...</h1>
            <p className="idle-subtitle">Calculando empaquetado óptimo 3D</p>
          </div>
        )}

        {status === 'SUCCESS' && result && (
          <div className="result-container">
            {/* Banner Semáforo */}
            <div className="traffic-banner success">
              <div className="banner-title">
                <CheckCircle2 size={36} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '10px' }} />
                EMPAQUETADO OPTIMIZADO - PEDIDO #{result.orderId}
              </div>
              <h2 className="banner-massive-text">UTILIZA: {result.boxModel}</h2>
              <p style={{ fontSize: '1.5rem', margin: '0.5rem 0 0 0' }}>{result.boxDetails}</p>
            </div>

            <div className="content-row">
              {/* Visualizador 3D MVP */}
              <div className="visualizer-card">
                <h3 className="visualizer-title">Guía de Colocación (3D)</h3>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Visualizer3D boxDimensions={result.boxDimensions} items={result.items} />
                </div>
              </div>

              {/* Acciones */}
              <div className="actions-column">
                <button className="btn-primary" onClick={resetState}>
                  SIGUIENTE PEDIDO
                  <div style={{ fontSize: '1rem', fontWeight: 'normal', marginTop: '0.5rem' }}>
                    (O escanea de nuevo)
                  </div>
                </button>
                <button className="btn-danger" onClick={() => alert('Incidencia reportada al supervisor.')}>
                  <AlertTriangle size={32} style={{ display: 'block', margin: '0 auto 0.5rem' }} />
                  REPORTAR PROBLEMA
                </button>
              </div>
            </div>
          </div>
        )}

        {status === 'ERROR' && (
          <div className="error-container">
            <div className="traffic-banner error">
              <AlertTriangle size={64} style={{ marginBottom: '1rem' }} />
              <h2 className="banner-massive-text">ERROR AL PROCESAR</h2>
              <p style={{ fontSize: '2rem', marginTop: '1rem' }}>{error.message}</p>
            </div>
            <button className="btn-primary" onClick={resetState} style={{ minHeight: '120px' }}>
              VOLVER A INTENTAR
            </button>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
