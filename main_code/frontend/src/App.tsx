/**
 * App — REDIMENSION Pick & Pack Main Interface.
 *
 * Industrial-grade packing station UI with barcode scanner integration,
 * traffic-light status feedback, and 3D box visualization.
 */

import { Suspense, lazy } from "react";
import { Package, AlertTriangle } from "lucide-react";

import { useScanner } from "./hooks/useScanner";
import { usePackingEngine } from "./hooks/usePackingEngine";
import { TrafficLightBanner } from "./components/UI/TrafficLightBanner";

// Lazy load the 3D visualizer for faster initial render
const OptimizedVisualizer = lazy(
  () => import("./components/3D/OptimizedVisualizer")
);

function App() {
  const { status, result, error, fetchOrderPacking, resetState } =
    usePackingEngine();
  const { inputRef, value, setValue, handleKeyDown } =
    useScanner(fetchOrderPacking);

  return (
    <div className="flex flex-col h-screen w-full bg-industrial-dark text-white font-sans">
      {/* Hidden input for barcode scanner capture */}
      {status !== "LOADING" && (
        <input
          id="scanner-input"
          ref={inputRef}
          type="text"
          className="absolute -top-[9999px] -left-[9999px] opacity-0"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus
          autoComplete="off"
          aria-label="Entrada de escáner de código de barras"
        />
      )}

      {/* Header */}
      <header
        id="main-header"
        className="flex justify-between items-center p-6 bg-industrial-panel border-b-2 border-[#0f172a]"
      >
        <div className="font-black text-3xl tracking-widest text-white flex items-center gap-4">
          <Package size={40} className="text-industrial-success" aria-hidden="true" />
          REDIMENSION Pick &amp; Pack
        </div>
        <div className="flex gap-8 text-2xl text-slate-400">
          <span>
            Operario: <strong className="text-white">Juan P.</strong>
          </span>
          <span>
            Turno: <strong className="text-white">Mañana</strong>
          </span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col justify-center items-center p-8 overflow-hidden">
        {/* IDLE State */}
        {status === "IDLE" && (
          <div className="flex flex-col items-center text-center gap-8 animate-fade-in">
            <Package className="text-slate-500" size={160} aria-hidden="true" />
            <h1 className="text-6xl font-black m-0 text-white">
              ESCANEA EL CÓDIGO DE BARRAS
            </h1>
            <p className="text-3xl text-slate-400 m-0">
              (El sistema está listo y esperando input)
            </p>
            <div className="mt-8 text-industrial-success font-bold text-2xl animate-pulse">
              [ Scanner Activo ]
            </div>
          </div>
        )}

        {/* LOADING State */}
        {status === "LOADING" && (
          <div className="flex flex-col items-center text-center gap-8 animate-fade-in">
            <h1 className="text-6xl font-black m-0 text-amber-500 animate-pulse">
              PROCESANDO...
            </h1>
            <p className="text-3xl text-slate-400 m-0">
              Calculando empaquetado óptimo 3D
            </p>
          </div>
        )}

        {/* SUCCESS State */}
        {status === "SUCCESS" && result && (
          <div className="w-full h-full flex flex-col gap-6 animate-fade-in">
            <TrafficLightBanner
              variant="success"
              title={`PEDIDO #${result.orderId} OPTIMIZADO`}
              massiveText={`UTILIZA: ${result.boxModel}`}
              subtitle={`Dimensiones: ${result.boxDetails}`}
            />

            <div className="flex flex-1 gap-8 mt-2 h-0">
              {/* 3D Visualizer */}
              <div className="flex-[2] bg-industrial-panel rounded-2xl overflow-hidden flex flex-col border-4 border-industrial-success">
                <h3 className="p-4 bg-industrial-success/20 text-industrial-success font-bold text-2xl border-b-4 border-industrial-success m-0">
                  Guía de Colocación (3D)
                </h3>
                <div className="flex-1 relative">
                  <Suspense
                    fallback={
                      <div className="flex items-center justify-center h-full text-2xl text-industrial-success animate-pulse">
                        Cargando Motor 3D...
                      </div>
                    }
                  >
                    <OptimizedVisualizer
                      boxDimensions={result.boxDimensions}
                      items={result.items}
                    />
                  </Suspense>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex-1 flex flex-col gap-6">
                <button
                  id="btn-next-order"
                  className="btn-massive bg-slate-200 text-slate-800 border-slate-300 flex-1 flex-col"
                  onClick={resetState}
                >
                  SIGUIENTE PEDIDO
                  <span className="text-xl font-normal mt-2">
                    (O escanea de nuevo)
                  </span>
                </button>
                <button
                  id="btn-report-problem"
                  className="btn-massive bg-industrial-danger border-industrial-dangerDark text-white h-[160px]"
                  onClick={() => alert("Incidencia reportada al supervisor.")}
                >
                  <AlertTriangle size={48} className="mb-2" aria-hidden="true" />
                  REPORTAR PROBLEMA
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ERROR State */}
        {status === "ERROR" && (
          <div className="w-full max-w-[1000px] flex flex-col gap-8 text-center animate-fade-in">
            <TrafficLightBanner
              variant="error"
              title="ERROR DE PROCESAMIENTO"
              massiveText="NO ENCONTRADO"
              subtitle={error || "El pedido no pudo ser verificado."}
            />
            <button
              id="btn-retry"
              className="btn-massive bg-slate-200 text-slate-800 border-slate-300"
              onClick={resetState}
            >
              VOLVER A INTENTAR
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
