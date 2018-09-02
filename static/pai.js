Highcharts.chart('container', {
        chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
        },
        title: {
                text: 'Pain market share in ShangHai'
        },
        tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
                pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                                style: {
                                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                                }
                        }
                }
        },
        series: [{
                name: 'Brands',
                colorByPoint: true,
                data: [{
                        name: 'Lai million Finn',
                        y: (16000)/390030,
                        sliced: true,
                        selected: true
                }, {
                        name: 'Celebrex',
                        y: (11000+5000+4200+5000+6300+7500+7200+5400)/390030
                }, {
                        name: 'Arcoxia',
                        y: (8000+4700+3900+400+2000+1300)/390030
                }, {
                        name: 'Heng Yang',
                        y: (7500+75+1100)/390030
                }, {
                        name: 'Loxonin',
                        y: (4800+2300+3100+10000+900+1000+8000+5000)/390030
                }, {
                        name: 'Ibuprofen',
                        y: (5200+1000+600+10000)/390030
                }, {
                        name: ' Difene',
                        y: (4500+2000+3200+1500+500+3200+13000)/390030
                }]
        }]
});