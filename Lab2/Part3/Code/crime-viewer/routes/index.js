// File: ./routes/index.js

var express = require('express');
var assert = require('assert');
var mongoose = require('mongoose');
var crimeModel = require('../models/crime.js');
var router = express.Router();

/* GET json data from the database */
router.get('/crime-data', function(req, res, next) {
    // Connect to the database
    mongoose.connect('mongodb://localhost/crime_data', {useNewUrlParser: true});

    var db = mongoose.connection;
    db.on('error', console.error.bind(console, 'connection error:'));

    // wait for the database to signal it is open
    db.once('open', function() {
        // get the crime data, store it so we can return it to the view
        // note: the {} denotes that we wwant mongodo to return ALL documents in the collection
        crimeModel.find({}, function (err, crimes) {
            assert.equal(null, err);

            // parse rhe returned results as json and return it in the response
            res.json(crimes);

            // close the connection
            mongoose.connection.close();
        }).select('category x_coordinate y_coordinate -_id'); // filter out the id from the returned documents, since js can't handle it
    });
});

/* GET home page. */
router.get('/', function(req, res, next) {
    // render the page
    res.render('index', { 
        title: 'Leaflet Crime Viewer', 
        dataset: 'crime_data'
    });
});

module.exports = router;
