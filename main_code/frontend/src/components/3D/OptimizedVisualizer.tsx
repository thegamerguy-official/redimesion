/**
 * OptimizedVisualizer — 3D Box Packing Visualization.
 *
 * Renders the selected container and all packed items using React Three Fiber.
 * Geometries and materials are memoized to prevent GPU memory leaks.
 */

import { useMemo, useEffect } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Edges } from "@react-three/drei";
import * as THREE from "three";

import type { PackingItem } from "../../types";

interface OptimizedVisualizerProps {
  boxDimensions: [number, number, number];
  items: PackingItem[];
}

/** Default color for items that don't specify one. */
const DEFAULT_ITEM_COLOR = "#3b82f6";

const OptimizedVisualizer = ({
  boxDimensions,
  items,
}: OptimizedVisualizerProps) => {
  // Memoize the outer box geometry
  const boxGeometry = useMemo(
    () => new THREE.BoxGeometry(...boxDimensions),
    [boxDimensions]
  );

  const boxMaterial = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: "#22c55e",
        transparent: true,
        opacity: 0.1,
      }),
    []
  );

  // Memoize item geometries to prevent re-instantiation every render
  const itemGeometries = useMemo(
    () => items.map((item) => new THREE.BoxGeometry(...item.dimensions)),
    [items]
  );

  // Memoize shared materials (one per unique color)
  const itemMaterials = useMemo(() => {
    const materials: Record<string, THREE.MeshStandardMaterial> = {};
    for (const item of items) {
      const color = item.color || DEFAULT_ITEM_COLOR;
      if (!materials[color]) {
        materials[color] = new THREE.MeshStandardMaterial({
          color,
          transparent: true,
          opacity: 0.9,
        });
      }
    }
    return materials;
  }, [items]);

  // Dispose GPU resources when geometries/materials change or component unmounts
  useEffect(() => {
    return () => {
      boxGeometry.dispose();
      boxMaterial.dispose();
      for (const geom of itemGeometries) {
        geom.dispose();
      }
      for (const mat of Object.values(itemMaterials)) {
        mat.dispose();
      }
    };
  }, [boxGeometry, boxMaterial, itemGeometries, itemMaterials]);

  return (
    <Canvas
      camera={{ position: [20, 20, 20], fov: 50 }}
      dpr={[1, 2]}
      performance={{ min: 0.5 }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 10]} intensity={1} />

      {/* Outer container wireframe */}
      <mesh geometry={boxGeometry} material={boxMaterial}>
        <Edges geometry={boxGeometry} color="#16a34a" />
      </mesh>

      {/* Packed items */}
      {items.map((item, index) => (
        <mesh
          key={`${item.id}-${index}`}
          position={item.position}
          geometry={itemGeometries[index]}
          material={itemMaterials[item.color || DEFAULT_ITEM_COLOR]}
        >
          <Edges geometry={itemGeometries[index]} color="#000000" />
        </mesh>
      ))}

      <OrbitControls
        enablePan={false}
        maxPolarAngle={Math.PI / 2}
        makeDefault
      />
    </Canvas>
  );
};

export default OptimizedVisualizer;
