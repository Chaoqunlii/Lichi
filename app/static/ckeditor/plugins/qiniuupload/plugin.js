CKEDITOR.plugins.add( 'qiniuUpload', {

    init: function( editor ) {
    	    editor.ui.addButton( 'Image', {
            label: '插入图片',
            command: 'openDialog',
            toolbar: 'insert'
        });
    }
});
