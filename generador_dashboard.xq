declare option output:method "html";
declare option output:html-version "5.0";
declare option output:encoding "UTF-8";

<html>
<head>
    <title>Dashboard Helpdesk</title>

    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px,1fr));
            gap: 20px;
        }

        .card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .prioridad-critica {
            border-left: 8px solid red;
        }

        .prioridad-alta {
            border-left: 8px solid orange;
        }

        .prioridad-media {
            border-left: 8px solid blue;
        }

        .prioridad-baja {
            border-left: 8px solid green;
        }

        .sla-alert {
            background-color: #ffe0e0;
            border: 1px solid red;
            padding: 10px;
            margin-top: 10px;
        }
    </style>

</head>

<body>

    <h1>Dashboard de Tickets</h1>

    <div class="grid-container">

    {
        for $ticket in collection("tickets")//ticket
        order by $ticket/fecha_creacion descending, $ticket/@prioridad descending

        return

        <div class="card prioridad-{lower-case(data($ticket/@prioridad))}">

            <h2>Ticket #{data($ticket/@id)}</h2>

            <h3>{data($ticket/titulo)}</h3>

            <p>
                <strong>Cliente:</strong>
                {data($ticket/cliente)}

                {
                if ($ticket/@cliente_enfadado = "si")
                then <span style="font-size:22px;"> ⚠️</span>
                else ()
                }
            </p>

            <p>
                <strong>Operador:</strong>
                {data($ticket/operador)}
            </p>

            <p>
                <strong>Fecha:</strong>
                {data($ticket/fecha_creacion)}
            </p>

            {
            if ($ticket/alerta_sla)
            then
                <div class="sla-alert">
                    🚨 SLA retrasado:
                    {data($ticket/alerta_sla)} días
                </div>
            else ()
            }

        </div>
    }

    </div>

</body>
</html>