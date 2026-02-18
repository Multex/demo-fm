# 📡 Guía Express de Modulación FM - 20 Minutos

## 📡 **CONCEPTOS FUNDAMENTALES DE FM**

### **¿Qué es FM?**
En FM (Frequency Modulation), la **frecuencia** de la portadora varía según el mensaje. A diferencia de AM donde varía la amplitud.

**La idea clave:** El mensaje m(t) "empuja" la frecuencia arriba y abajo alrededor de fc.

---

## 🎛️ **CÓMO AFECTAN LOS SLIDERS (MUY IMPORTANTE)**

### **1. Frecuencia portadora (fc) - 10 kHz por defecto**
- **Qué es:** La frecuencia "base" antes de modular
- **Si SUBES fc:**
  - Gráfica 2: La línea negra (fc) sube
  - Gráfica 3: La señal s(t) oscila MÁS RÁPIDO (más onditas)
  - Gráfica 4: La portadora oscila más rápido
- **Analogía radio:** Es como cambiar de 88.5 FM a 105.7 FM en tu radio

### **2. Frecuencia del mensaje (fm) - 200 Hz por defecto**
- **Qué es:** Qué tan rápido cambia tu mensaje (la señal de audio/datos)
- **Si SUBES fm:**
  - Gráfica 1: m(t) tiene más ciclos por segundo (se "comprime")
  - Gráfica 2: fi(t) oscila más rápidamente
  - β BAJA (porque β = Δf/fm)
  - Ancho de banda de Carson SUBE
- **Analogía:** Voz aguda (fm alto) vs voz grave (fm bajo)

### **3. Amplitud del mensaje (Am) - 1V por defecto**
- **Qué es:** "Volumen" del mensaje
- **Si SUBES Am:**
  - Gráfica 1: m(t) tiene mayor voltaje (±Am)
  - Δf SUBE (Δf = kf × Am)
  - β SUBE (más desviación)
  - Gráfica 2: fi(t) se aleja MÁS de fc (mayor excursión)
  - Gráfica 3: s(t) varía de frecuencia más dramáticamente
- **Analogía:** Hablar más fuerte (más Am) → la señal FM se "desvía" más

### **4. Sensibilidad kf - 5 kHz/V por defecto**
- **Qué es:** "Ganancia" del modulador. Cuántos Hz de desviación por cada voltio de m(t)
- **Si SUBES kf:**
  - Δf SUBE (Δf = kf × Am)
  - β SUBE
  - Gráfica 2: fi(t) se aleja MUCHO más de fc
  - Gráfica 3: s(t) tiene variaciones de frecuencia más extremas
  - **CUIDADO:** Puedes causar aliasing si (fc + Δf) ≥ Fs/2
- **Analogía:** Subir el "volumen del desvío de frecuencia"

### **5. Armónicos H - 1 por defecto**
- **Qué es:** Señales no senoidales tienen armónicos (3fm, 5fm, 7fm...)
- **Si SUBES H:**
  - Solo afecta el ancho de banda de Carson (B)
  - fm,max = H × fm → B = 2(Δf + H×fm)
  - **No cambia las gráficas**, solo el cálculo de ancho de banda
- **Por qué importa:** Una cuadrada tiene muchos armónicos; si H=1 subestimas el ancho de banda real

### **6. Frecuencia de muestreo (Fs) - 200 kHz por defecto**
- **Qué es:** Muestras por segundo que tomas
- **Si SUBES Fs:**
  - Gráficas se ven más suaves (más puntos)
  - Menos riesgo de aliasing
  - Mayor costo computacional
- **Regla de oro:** Fs ≥ 2(fc + Δf) para evitar aliasing

---

## 📊 **LAS 5 MÉTRICAS CLAVE**

### **Δf (Desviación de frecuencia)**
```
Δf = kf × Am
```
**Qué significa:** Cuánto se "aleja" la frecuencia de fc
**Ejemplo:** Si Δf = 5 kHz y fc = 10 kHz, entonces fi oscila entre 5-15 kHz

### **β (Índice de modulación)**
```
β = Δf / fm
```
- **β < 1:** FM de banda estrecha (Narrowband FM)
- **β > 1:** FM de banda ancha (Wideband FM)
- **Radio comercial FM:** β ≈ 5 típicamente

### **fc (Frecuencia portadora)**
```
fc = 10 kHz (por defecto)
```
**Qué significa:** Frecuencia central de la señal FM
**Ejemplo:** En radio FM comercial: 88-108 MHz

### **fm (Frecuencia del mensaje)**
```
fm = 200 Hz (por defecto)
```
**Qué significa:** Frecuencia de la señal moduladora
**Ejemplo:** Audio humano: 20 Hz - 20 kHz

### **B (Ancho de banda de Carson)**
```
fm,max = H × fm
B ≈ 2(Δf + fm,max)
```
**Qué significa:** Cuánto espectro necesitas para transmitir sin pérdida significativa
**Ejemplo:** Si Δf = 5 kHz y fm,max = 200 Hz → B = 10.4 kHz

---

## 🔍 **ANÁLISIS DE CAMBIOS EN EL CÓDIGO**

### **Cambio 1: `np.linspace` en vez de `np.arange` (líneas 224-226)**
```python
N = int(Fs * dur)
t = np.linspace(0, dur, N, endpoint=False)
dt = 1.0 / Fs
```
**Por qué es mejor:**
- `arange` puede tener errores de redondeo en punto flotante
- `linspace` garantiza exactamente N muestras
- Más predecible y robusto numéricamente

### **Cambio 2: Mostrar muestras por período (líneas 275-280)**
```python
mpp = Fs / fm  # muestras por período
if mpp < 10:
    st.info(f"solo {mpp:.1f} muestras por período...")
```
**Por qué importa:**
- Si tienes pocas muestras por período (ej: 5), la onda se ve pixelada
- Mínimo recomendado: 10 muestras por período para visualización suave
- Ayuda a diagnosticar problemas de visualización

### **Cambio 3: Fórmulas explícitas (líneas 192-199)**
Agregaste las expresiones matemáticas exactas de cada forma de onda:
```latex
x_cuad(t) = sgn[sin(2πfm·t)]
x_diente(t) = 2((t/T) - floor(t/T + 1/2)), T = 1/fm
x_tri(t) = 2|2((t/T) - floor(t/T + 1/2))| - 1
m(t) = Am · x(t)
```
**Por qué es mejor:** Excelente para defensa académica, muestra rigor matemático

---

## 🎯 **EXPERIMENTOS PARA ENTENDER FM**

### **Experimento 1: Efecto de kf**
1. Pon kf = 0.1 kHz/V → Gráfica 3 casi no varía (FM débil)
2. Pon kf = 50 kHz/V → Gráfica 3 varía MUCHO (FM fuerte)
3. **Conclusión:** kf controla la "intensidad" de la modulación

### **Experimento 2: Efecto de fm**
1. Pon fm = 50 Hz → Gráfica 1 lenta, β alto (β = Δf/fm)
2. Pon fm = 2000 Hz → Gráfica 1 rápida, β bajo
3. **Conclusión:** fm controla qué tan "rápido" cambia el mensaje

### **Experimento 3: Aliasing (¡IMPORTANTE!)**
1. Pon fc = 100 kHz, kf = 50 kHz/V, Am = 2V → Δf = 100 kHz
2. fc + Δf = 200 kHz, pero Fs/2 = 100 kHz (con Fs = 200 kHz)
3. **Verás error rojo:** ¡ALIASING!
4. Sube Fs a 500 kHz → Se arregla
5. **Lección:** Siempre verifica que (fc + Δf) < Fs/2

### **Experimento 4: Formas de onda y armónicos**
1. **Cuadrada:** Bordes abruptos → muchos armónicos → necesitas H alto (7, 9, 11...)
2. **Triangular:** Más suave → menos armónicos → H=3 o H=5 suele bastar
3. **Diente de sierra:** Intermedio entre cuadrada y triangular
4. **Observa:** Cambia H de 1 a 15 y mira cómo sube el ancho de banda de Carson

### **Experimento 5: Beta (β) - Banda estrecha vs ancha**
1. Pon kf = 0.5, Am = 1, fm = 500 → β ≈ 1 (banda estrecha)
2. Pon kf = 20, Am = 1, fm = 200 → β ≈ 100 (banda ancha)
3. **Observa:** En gráfica 2, mayor β = mayor excursión de fi(t)

---

## 🎓 **PUNTOS CLAVE PARA DEFENDER**

### **1. ¿Por qué usar Carson para no senoidales?**
- Señales no senoidales tienen armónicos (3fm, 5fm, 7fm...)
- Una onda cuadrada tiene infinitos armónicos impares
- fm,max = H×fm captura esos armónicos en el cálculo de ancho de banda
- Si usas solo fm (como en senoidales), subestimas el ancho de banda real
- **Ejemplo defendible:** "Para una cuadrada de 200 Hz con H=7, consideramos armónicos hasta 1.4 kHz"

### **2. ¿Qué es fi(t) y por qué importa?**
```
fi(t) = fc + kf·m(t)
```
- La frecuencia instantánea "sigue" al mensaje
- Es la derivada de la fase: fi(t) = (1/2π)·dφ/dt
- En la gráfica 2 puedes VER cómo la frecuencia sube y baja
- **Ejemplo defendible:** "Cuando m(t) = +1V y kf = 5 kHz/V, la frecuencia sube 5 kHz sobre fc"

### **3. ¿Cómo se genera s(t)?**
```
φ(t) = 2πfc·t + 2πkf·∫m(τ)dτ
s(t) = cos(φ(t))
```
- Primero integras el mensaje (línea 252: `np.cumsum(m) * dt`)
- La integral acumula el "área bajo la curva" de m(t)
- Esa integral se suma a la fase de la portadora
- **Ejemplo defendible:** "Usamos cumsum para aproximar la integral en tiempo discreto"

### **4. ¿Por qué la portadora desaparece en el espectro FM?**
- Para β > 2.4, la componente espectral en fc casi desaparece
- Esto se explica con funciones de Bessel: J₀(β) → 0 cuando β es grande
- La energía se redistribuye en bandas laterales
- **Ejemplo defendible:** "Con β = 5, la portadora tiene potencia casi nula según J₀(5) ≈ -0.18"

### **5. ¿Por qué FM es mejor que AM para radio?**
- **Inmunidad al ruido:** El ruido afecta la amplitud, no la frecuencia
- **Mejor calidad de audio:** Mayor ancho de banda → mejor fidelidad
- **Captura del más fuerte:** La señal más fuerte "captura" el receptor
- **Ejemplo defendible:** "FM comercial usa Δf = 75 kHz para alta fidelidad de audio"

---

## ⚡ **CHEAT SHEET RÁPIDO**

### **Tabla de efectos**
| Parámetro | ↑ Aumenta | Efecto principal | Métrica afectada |
|-----------|-----------|------------------|------------------|
| **fc** | → | s(t) oscila más rápido | fc↑ |
| **fm** | → | m(t) más comprimida | β↓, B↑ |
| **Am** | → | m(t) mayor amplitud | Δf↑, β↑, B↑ |
| **kf** | → | Mayor sensibilidad | Δf↑, β↑, B↑ |
| **H** | → | Más armónicos considerados | Solo B↑ |
| **Fs** | → | Gráficas más suaves | Calidad visual |

### **Ecuaciones maestras**
```
Δf = kf × Am
β = Δf / fm
B = 2(Δf + H×fm)
fi(t) = fc + kf·m(t)
φ(t) = 2πfc·t + 2πkf·∫m(τ)dτ
s(t) = cos(φ(t))
```

### **Valores típicos en radio FM comercial**
- **fc:** 88-108 MHz (banda FM)
- **Δf:** ±75 kHz (desviación máxima permitida)
- **fm:** 50 Hz - 15 kHz (audio)
- **β:** ≈ 5 (75 kHz / 15 kHz)
- **B:** ≈ 180 kHz (ancho de canal = 200 kHz)

### **Reglas de diseño**
1. **Anti-aliasing:** Fs ≥ 2(fc + Δf)
2. **Visualización suave:** Fs/fm ≥ 10 (muestras por período)
3. **Estabilidad visual:** Fs ≥ 10·fc
4. **Armónicos significativos:** H ≥ 5 para cuadradas, H ≥ 3 para triangulares

---

## 🚀 **TIPS PARA LA PRESENTACIÓN**

### **Demo en vivo recomendada:**
1. **Inicio:** Valores por defecto, explica las 4 gráficas
2. **Sube kf de 5 a 30:** Muestra cómo Δf y β suben, fi(t) se "ensancha"
3. **Cambia forma de onda:** Cuadrada → Triangular → Diente de sierra
4. **Sube H de 1 a 11:** Muestra cómo solo B cambia
5. **Provoca aliasing:** fc=100, kf=50, Am=2 → ERROR ROJO
6. **Arréglalo:** Sube Fs a 500 kHz → Se arregla

### **Preguntas típicas y respuestas:**

**P: ¿Por qué no usar solo fm en vez de H·fm?**
R: Porque señales no senoidales tienen armónicos. Una cuadrada de 200 Hz tiene componentes en 600 Hz, 1 kHz, 1.4 kHz... Si solo usas 200 Hz, subestimas el ancho de banda.

**P: ¿Qué pasa si β < 1?**
R: FM de banda estrecha. El espectro es similar a AM. Se usa en comunicaciones de voz donde se prioriza ancho de banda sobre calidad.

**P: ¿Por qué integrar m(t)?**
R: Porque FM modula la frecuencia instantánea fi = fc + kf·m. Como fi = dφ/dt, entonces φ = ∫fi·dt = 2πfc·t + 2πkf·∫m·dt.

**P: ¿Qué es mejor, AM o FM?**
R: FM para calidad de audio (radio, música). AM para largo alcance (onda corta, aviación). FM es inmune al ruido de amplitud.

---

## 📚 **REFERENCIAS ÚTILES**

- **Clark S. Hess:** "Sistemas de Comunicaciones" - Libro de referencia citado en el código
- **Regla de Carson:** J.R. Carson (1922) - "Notes on the theory of modulation"
- **Funciones de Bessel:** Explican el espectro de FM (Jn(β))
- **Teorema de Nyquist:** Harry Nyquist (1928) - Base del teorema de muestreo

---

## 🎯 **ÚLTIMO CONSEJO**

**No memorices fórmulas, entiende la física:**
- m(t) grande → fi se aleja mucho de fc → s(t) cambia de frecuencia rápidamente
- fm alto → m(t) cambia rápido → fi(t) oscila rápidamente → más ancho de banda
- kf alto → "amplificador" de la desviación → mayor Δf

**La clave de FM:** La información está en cuánto varía la frecuencia, no en la amplitud.

---

¡Buena suerte en tu presentación! 🚀
