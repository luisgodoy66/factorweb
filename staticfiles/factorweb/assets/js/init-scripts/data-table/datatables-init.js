(function ($) {
    //    "use strict";

    /*  Bootstrap Table Init
    ---------------------*/

    // Inicialización automática de todas las tablas con clase bootstrap-table-auto
    $('.bootstrap-table-auto').bootstrapTable({
        locale: "es-EC",
        pagination: true,
        search: true,
        showSearchClearButton: true,
        showColumns: true,
        // showRefresh: true,
        showExport: true,
        exportOptions: {
            type: ['json', 'xml', 'csv', 'txt', 'excel', 'pdf'],
            ignoreColumn: [-1] // Ignorar última columna (acciones)
        },
        pageSize: 10,
        pageList: [10, 25, 50, 100, 'Todos'],
        searchAlign: 'left',
        buttonsAlign: 'right',
        toolbar: '',
        classes: 'table table-hover table-bordered',
        theadClasses: 'bg-white'
    });

    // Configuración específica para tablas con export (compatibilidad con templates existentes)
    $('#bootstrap-data-table-export').bootstrapTable({
        locale: "es-EC",
        pagination: true,
        search: true,
        showSearchClearButton: true,
        showColumns: true,
        // showRefresh: true,
        showExport: true,
        exportOptions: {
            type: ['json', 'xml', 'csv', 'txt', 'excel', 'pdf'],
            ignoreColumn: [-1] // Ignorar última columna (acciones)
        },
        pageSize: 10,
        pageList: [10, 25, 50, 100, 'Todos'],
        searchAlign: 'left',
        buttonsAlign: 'right',
        classes: 'table table-hover table-bordered',
        theadClasses: 'bg-white'
    });

})(jQuery);
