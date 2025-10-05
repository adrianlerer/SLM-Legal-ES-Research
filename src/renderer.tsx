import { jsxRenderer } from 'hono/jsx-renderer'

export const renderer = jsxRenderer(({ children }) => {
  return (
    <html lang="es">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>SLM Legal Spanish - Análisis Legal Inteligente</title>
        <meta name="description" content="Sistema Inteligente de Análisis Legal y Compliance para Documentos Académicos y Corporativos" />
        
        {/* Tailwind CSS */}
        <script src="https://cdn.tailwindcss.com"></script>
        
        {/* Font Awesome Icons */}
        <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet" />
        
        {/* Custom Styles */}
        <link href="/static/styles.css" rel="stylesheet" />
        
        {/* Favicon */}
        <link rel="icon" type="image/x-icon" href="/static/favicon.ico" />
      </head>
      <body className="font-sans antialiased">
        {children}
        
        {/* External Libraries */}
        <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/dayjs@1.11.10/dayjs.min.js"></script>
        
        {/* Custom JavaScript */}
        <script src="/static/app.js"></script>
      </body>
    </html>
  )
})