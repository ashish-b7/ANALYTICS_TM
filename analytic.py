from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'asdd'
loaded_data = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global loaded_data
    file = request.files['file']
    if file:
        loaded_data = pd.read_excel(file)
        columns = list(loaded_data.columns)
        return render_template('upload.html', columns=columns)
    return render_template('index.html', error="File not provided.")

@app.route('/plot', methods=['POST'])
def plot():
    if loaded_data is None:
        return render_template('upload.html', error="No data loaded.")
    
    selected_columns = request.form.getlist('columns')
    if not selected_columns:
        return render_template('upload.html', error="Select at least one column.")

    chart_type = request.form.get('chart_type', 'bar')

    try:
        if chart_type == 'bar':
            plotly_fig = render_bar_chart(selected_columns)
        elif chart_type == 'line':
            plotly_fig = render_line_chart(selected_columns)
        elif chart_type == 'pie':
            plotly_fig = generate_pie_chart(selected_columns)
        else:
            raise ValueError("Invalid chart type.")
    except Exception as e:
        return render_template('upload.html', error=f"Error generating plot: {str(e)}")

    try:
        plotly_html = plotly_fig.to_html(full_html=False)
    except Exception as e:
        return render_template('upload.html', error=f"Error converting plot to HTML: {str(e)}")

    return render_template('plotly_template.html', plotly_html=plotly_html)


def render_bar_chart(selected_columns):
    if len(selected_columns) != 2:
        return render_template('upload.html', error="Select exactly two columns for bar chart.")

    group_column, sum_column = selected_columns

    grouped_data = loaded_data.groupby(group_column)[sum_column].sum().reset_index()

    fig = px.bar(grouped_data, x=group_column, y=sum_column, 
                 title=f'Bar Chart of Total {sum_column} by {group_column}',
                 labels={sum_column: f"Total {sum_column}"})
    return fig


def render_line_chart(selected_columns):
    if len(selected_columns) != 2:
        return render_template('upload.html', error="Select exactly two columns for line chart.")

    x_column, y_column = selected_columns

    grouped_data = loaded_data.groupby(x_column)[y_column].mean().reset_index()

    fig = px.line(grouped_data, x=x_column, y=y_column, 
                  title=f'Line Chart of Average Values for {y_column} by {x_column}',
                  labels={y_column: f'Average {y_column}'})
    return fig

def generate_pie_chart(selected_columns):
    fig = px.pie(loaded_data, names=selected_columns[0], values=selected_columns[1], 
                 title=f'Pie Chart for {selected_columns[0].capitalize()} ({selected_columns[1].capitalize()})')
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)
