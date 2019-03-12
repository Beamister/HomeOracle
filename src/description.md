# Home Oracle

Welcome to Home Oracle, the online tool for analysing how changes in your area effects the value of your home. Through this tool you can also add new data sources and models for making use of the data. There is also a handy little viewer for taking a closer look at your data.

## Property View

This is the main page for predicting changes in property value, just input the current value of your property, the current values that describe your area and the values you expect your area to change to. Then, when you click predict, the selected model will be used to make a prediction about how your property value will change.

## Model Editor

You can use the model editor to add new machine learning models for interpretation on the property view. As well as choosing the model settings, you can choose which dataset to use and which fields to use from it. Once the model has been generated, head over to the model viewer to train the model.

## Model View

Here you can see existing models, their inputs and dependencies. You can also delete models and send them for training, once they've finished training then their status will be updated.

## Source View

If you want to add a new data source then here you can, just give the source a name and input the URL to download from, URL instructions are below, and the rest of the source settings.

## RDS / Dynamo View

These views are for taking a look at the contents of the RDS and Dynamo data stores.

## URL Instructions

When you specify a URL in the sources input, you will need to give a base static URL. Then, if part of the URL is dependent on the date, a date token can be specified. A date token is preceded by -d, and uses D,M, and Y to mark the different parts of the date. Any static parts of the date must be enclosed in quotation marks, e.g. "/". Any additional parts of the URL after a date token needed to be marked as static tokens using -s.
