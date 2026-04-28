import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🧹 Limpiando base de datos...');
  await prisma.orderItem.deleteMany();
  await prisma.orderHistory.deleteMany();
  await prisma.boxType.deleteMany();
  await prisma.sKU.deleteMany();
  await prisma.tenant.deleteMany();

  console.log('🏢 Creando Tenant (Cliente de prueba)...');
  const tenant = await prisma.tenant.create({
    data: { name: 'Logística Elche S.L.' }
  });

  console.log('📦 Creando Catálogo de Cajas...');
  await prisma.boxType.createMany({
    data: [
      { tenantId: tenant.id, name: 'Caja A', length_cm: 40, width_cm: 30, height_cm: 20, grammage_kg_m2: 0.5 },
      { tenantId: tenant.id, name: 'Sobre Kraft', length_cm: 25, width_cm: 17, height_cm: 3, grammage_kg_m2: 0.2 },
      { tenantId: tenant.id, name: 'Caja Cúbica', length_cm: 25, width_cm: 20, height_cm: 15, grammage_kg_m2: 0.5 }
    ]
  });

  console.log('👕 Creando Catálogo de Productos (SKUs)...');
  await prisma.sKU.createMany({
    data: [
      { tenantId: tenant.id, skuCode: 'USB-001', name: 'Memoria USB 64GB', length_cm: 10, width_cm: 5, height_cm: 1, weight_g: 50 },
      { tenantId: tenant.id, skuCode: 'TSHIRT-01', name: 'Camiseta Algodón', length_cm: 25, width_cm: 20, height_cm: 2, weight_g: 200 },
      { tenantId: tenant.id, skuCode: 'PANTS-01', name: 'Pantalón Vaquero', length_cm: 30, width_cm: 20, height_cm: 4, weight_g: 500 },
      { tenantId: tenant.id, skuCode: 'BELT-01', name: 'Cinturón Cuero', length_cm: 15, width_cm: 15, height_cm: 3, weight_g: 150 },
      { tenantId: tenant.id, skuCode: 'BOOK-01', name: 'Libro Tapa Dura', length_cm: 23, width_cm: 15, height_cm: 3, weight_g: 600 }
    ]
  });

  console.log('✅ ¡Base de datos poblada con éxito!');
  console.log(`🔑 ID de tu Tenant (Cliente): ${tenant.id}`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });