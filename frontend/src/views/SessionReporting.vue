<template>
  <div>
    <p>Received Variable: {{ sessionID }}</p>
  </div>

  <v-main>
    <div class="chart-container">
      <canvas id="scatterChart"></canvas>
    </div>
  </v-main>
</template>

<script>
import Papa from 'papaparse'
import {
  Chart,
  ScatterController,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js'

export default {
  data() {
    return {
      sessionID: null,
    }
  },

  mounted() {
    this.sessionID = this.$route.params.id

    Chart.register(
      ScatterController,
      LinearScale,
      PointElement,
      Tooltip,
      Legend,
      Title,
    )

    const main = async () => {
      //path to files currently in frontend/public dir
      const csvData = [
        '/Task 1_keyboard_data.csv',
        '/Task 1_mouse_clicks_data.csv',
        '/Task 1_mouse_movement_data.csv',
        '/Task 1_mouse_scroll_data.csv',
      ]

      //y-axis labels
      const labels = [
        'Keyboard Inputs',
        'Mouse Clicks',
        'Mouse Movement',
        'Mouse Scrolls',
      ]

      //colors for the different measurement types
      const colors = ['#342d82', '#5f46bc', '#ac81bf', '#d4bfdd']

      //for unique tooltip info based on measurement type
      const tooltipFormats = [
        formatKeyboardData,
        formatMouseData, //for clicks
        formatMouseData, //for movement
        formatMouseData, //for scrolls
      ]

      const datasets = await createDatasets(
        csvData,
        labels,
        colors,
        tooltipFormats,
      )

      const data = { datasets }

      const config = {
        type: 'scatter',
        data: data,
        options: {
          responsive: true,
          maintainAspectRation: true,
          aspectRatio: 2,
          plugins: {
            title: {
              display: true,
              text: 'Task 1', //need to be dynamic eventually
              color: 'black',
              font: {
                size: 32,
                weight: 'bold',
              },
            },
            tooltip: {
              callbacks: {
                label: getTooltip,
              },
            },
          },
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Time (s)',
                color: 'black',
                font: {
                  size: 20,
                  weight: 'bold',
                },
              },
              type: 'linear',
              min: 0,
              position: 'bottom',
            },
            y: {
              display: true,
              title: {
                display: true,
                text: 'Measurement Type',
                color: 'black',
                font: {
                  size: 20,
                  weight: 'bold',
                },
              },
              type: 'linear',
              min: 0,
              max: 5,
              ticks: {
                callback: function (val) {
                  return labels[val - 1] || ''
                },
                stepSize: 1,
                color: 'black',
              },
            },
          },
        },
      }

      //render chart
      const ctx = document.getElementById('scatterChart').getContext('2d')
      new Chart(ctx, config)
    }

    //special tooltip formatting for mouse stuff
    const formatMouseData = measurement => {
      return [
        `Real Time: ${measurement.Time}`,
        `Task Time: ${measurement.running_time}s`,
        `x-coord: ${measurement.x}`,
        `y-coord: ${measurement.y}`,
      ]
    }

    //special tooltip formatting for keyboard stuff
    const formatKeyboardData = measurement => {
      return [
        `Real Time: ${measurement.Time}`,
        `Task Time: ${measurement.running_time}s`,
        `Key Pressed: ${measurement.keys}`,
      ]
    }

    //get unique tooltip labels
    const getTooltip = context => {
      const datasetIndex = context.datasetIndex //index of dataset
      const indexP = context.dataIndex //index of point
      const dataset = context.chart.data.datasets[datasetIndex] //getting actual dataset
      const measurement = dataset.measurements[indexP] //grabbing measurement data now

      return dataset.tooltipFormat(measurement) //formatting the data
    }

    //DOC used: https://www.papaparse.com/docs#local-files
    //purpose is to parse a csv
    const readCSV = file => {
      return new Promise((resolve, reject) => {
        Papa.parse(file, {
          download: true, //URL passed from which we download the file and parse its contents
          header: true, //skip column headers
          skipEmptyLines: true, //if blank lines in csv
          complete: results => resolve(results.data), //receives the parse results when complete
          error: err => reject(err), //if error encountered
        })
      })
    }

    const createDatasets = async (csvData, labels, colors, tooltipFormats) => {
      const datasets = []

      //going through each CSV
      for (let i = 0; i < csvData.length; i++) {
        const data = await readCSV(csvData[i]) //parse current csv w/ fxn above

        const currDataset = {
          //creating array and initializing w/ unique values based on the current iteration/csv
          label: labels[i],
          data: [],
          backgroundColor: colors[i],
          pointRadius: 5,
          measurements: data,
          tooltipFormat: tooltipFormats[i], //keyboard & mouse have diff data points so must account for this
        }

        //going through each row
        for (let j = 0; j < data.length; j++) {
          const tempR = data[j]
          currDataset.data.push({
            x: parseFloat(tempR.running_time), //associated with time relative to task start
            y: i + 1, //height is a set constant here and not indicative of an actual measurement
          })
        }

        datasets.push(currDataset) //adding dataset to datasets array
      }

      return datasets
    }

    main()
  },
}
</script>

<style>
.chart-container {
  width: 100%;
  height: 100%;
  aspect-ratio: 2;
}
</style>
